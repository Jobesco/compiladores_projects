# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GrammarParser import GrammarParser
else:
    from GrammarParser import GrammarParser

import sys
err = sys.stderr.write
def printf(string, *args):
    sys.stdout.write(string % args)

import struct
import math
# Função utilizada para transformar um valor float para um valor hexadecimal 
# (o equivalente em hexadecimal dos valores dos bits de um float)
def float_to_hex(f):
    float_hex = hex(struct.unpack('<Q', struct.pack('<d', f))[0])
    if (int(float_hex[10],16) % 2 != 0):
        if (float_hex[10] == 'f'):
            float_hex = float(math.ceil(f))
        else:
            float_hex = float_hex[:10] + hex(int(float_hex[10],16) + 1)[2] + "0000000"

    else: 
        float_hex = float_hex[:11] + "0000000"
    return float_hex


# retorne Type.INT, etc para fazer checagem de tipos
class Type:
    VOID = "void"
    INT = "int"
    FLOAT = "float"
    STRING = "char *"

def llvm_type(tyype):
    if tyype == Type.VOID:
        return "void"
    if tyype == Type.INT:
        return "i32"
    if tyype == Type.FLOAT:
        return "float"

f = open("output.ll", "w") #? use f.write()

class GrammarCheckerVisitor(ParseTreeVisitor):
    ids_defined = {} # Dicionário para armazenar as informações necessárias para cada identifier definido
    inside_what_function = "" # String que guarda a função atual que o visitor está visitando. Útil para acessar dados da função durante a visitação da árvore sintática da função.
    in_bifurcation = False
    param_number = 0 # ? numero de parametros que a funcao tem, para q n usemos seus devidos registradores
    used_regs = {} # ? numero reg : (tipo, reg variavel associado OU expressao associada)
    in_return_function_check = False
    dont_print = False

    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx:GrammarParser.FiileContext):
        return self.visitChildren(ctx)


     # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx:GrammarParser.Function_definitionContext):
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()
        

        f.write('define '+llvm_type(tyype)+' @'+name+'(')

        self.inside_what_function = name
        params = self.visit(ctx.arguments())
        self.param_number = len(params)
        self.ids_defined[name] = tyype, params, None # ? 0 -> tyype ; 1 -> params

        f.write(') {\n')
        self.used_regs = {}
        self.visit(ctx.body())
        self.inside_what_function = None
        self.param_number = 0
        self.used_regs = {}

        f.write('}\n\n')
        return


    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx:GrammarParser.BodyContext):
        # ! primeirissima coisa: faz toda a alocação loucura lá pra cada parâmetro passado
        params = self.ids_defined.get(self.inside_what_function)[1] # ? 0 -> tipo ; 1 -> nome ; 2 -> registrador
        
        for i in range(len(params)):
            f.write('\t%' + params[i][1] + ' = alloca ' + llvm_type(params[i][0]) + ', align 4\n' )
            f.write('\tstore ' + llvm_type(params[i][0]) + ' ' + params[i][2] + ', ' +  llvm_type(params[i][0]) + '* %' + params[i][1] + ', align 4\n' )

            params[i] = (params[i][0], params[i][1], '%'+params[i][1])
        
        return_temp = self.ids_defined.get(self.inside_what_function)
        return_temp = (return_temp[0] , params, return_temp[2])
        self.ids_defined[self.inside_what_function] = return_temp

        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx:GrammarParser.StatementContext):
        # ? se o statement tiver um return, e nele, uma function call, a gt atribui o valor a um reg numerico e escreve :)
        if(ctx.RETURN() and ctx.expression()):
            if(ctx.expression().function_call()):
                self.in_return_function_check = True
                self.dont_print = True

        self.visitChildren(ctx)

        if(ctx.RETURN() and ctx.expression()):
            if(ctx.expression().function_call()):
                self.in_return_function_check = False
                self.dont_print = False

        if(ctx.RETURN()):
            if(ctx.expression()):
                if(ctx.expression().function_call()):
                    tyype, params, ignore = self.ids_defined.get(ctx.expression().function_call().identifier().getText())

                    self.param_number = self.param_number + 1
                    f.write('\t%' + str(self.param_number) + ' = call ' + llvm_type(tyype) + ' @' + ctx.expression().function_call().identifier().getText() + '(')
                    for i in range(len(params)):
                        self.in_return_function_check = True
                        tyype, value, ignore = self.visit(ctx.expression().function_call().expression(i))
                        self.in_return_function_check = False
                        if i: f.write(' ' + llvm_type(params[i][0]) + ' ' + str(value))
                        else: f.write(llvm_type(params[i][0]) + ' ' + str(value))
                    f.write(')\n')

                    self.used_regs[self.param_number] = (tyype, ctx.expression().getText())

                    

                    # ? verifica se a expressão retornada é void
                    if(self.ids_defined[ctx.expression().function_call().identifier().getText()][0] == Type.VOID):
                        token = ctx.RETURN().getPayload()
                        print('ERROR: trying to return void expression from function \'{}\' in line {} and column {}'.format(str(self.inside_what_function),str(token.line),str(token.column)))
                    # ? se a função é float num return de int
                    elif(self.ids_defined.get(ctx.expression().function_call().identifier().getText())[0] == Type.FLOAT and self.ids_defined.get(self.inside_what_function)[0] == Type.INT):
                        token = ctx.RETURN().getPayload()
                        print('WARNING: possible loss of information returning float expression from int function \'{}\' in line {} and column {}'.format(self.inside_what_function,str(token.line),str(token.column)))
        
                if ctx.expression().identifier():
                    tyype, expr, ignore = self.ids_defined.get(ctx.expression().identifier().getText())
                    # print(self.ids_defined.get(ctx.expression().identifier().getText()), '<<<<<<<<<<<<<<<') #DEBUG
                    # ? aloca um reg numerico p usar
                    self.param_number = self.param_number + 1
                    f.write('\t%' + str(self.param_number) + ' = load ' + llvm_type(tyype) + ', ' + llvm_type(tyype) + '* %' + ctx.expression().identifier().getText() + ', align 4\n')

                    self.used_regs[self.param_number] = (tyype, ctx.expression().identifier().getText()) # ? tipo, reg var associado ou expressao associada

                # ? armazena a expressão relacionada antes
                # pega ela no retorno
                for i, reg in enumerate(self.used_regs):
                    temp = self.used_regs.get(reg)
                    if temp[1] == ctx.expression().getText():
                        # print('achei') #DEBUG
                        f.write('\tret ' + llvm_type(temp[0]) + ' %' + str(reg) + '\n')
                        break
            else:
                f.write('\tret void\n')
        
        # ? se a função void tiver return
        if(ctx.RETURN() and self.ids_defined[self.inside_what_function][0] == Type.VOID):
            token = ctx.RETURN().getPayload() # Obtém o token referente à uma determinada regra léxica (neste caso, IDENTIFIER)
            print("ERROR: trying to return a non void expression from void function \'{}\' in line {} and column {}".format(self.inside_what_function,str(token.line), str(token.column)))


    # Visit a parse tree produced by GrammarParser#if_statement.
    def visitIf_statement(self, ctx:GrammarParser.If_statementContext):
        self.in_bifurcation = True
        self.visitChildren(ctx)
        self.in_bifurcation = False


    # Visit a parse tree produced by GrammarParser#else_statement.
    def visitElse_statement(self, ctx:GrammarParser.Else_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_loop.
    def visitFor_loop(self, ctx:GrammarParser.For_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_initializer.
    def visitFor_initializer(self, ctx:GrammarParser.For_initializerContext):
        self.in_bifurcation = True
        self.visitChildren(ctx)
        self.in_bifurcation = False


    # Visit a parse tree produced by GrammarParser#for_condition.
    def visitFor_condition(self, ctx:GrammarParser.For_conditionContext):
        self.in_bifurcation = True
        self.visitChildren(ctx)
        self.in_bifurcation = False


    # Visit a parse tree produced by GrammarParser#for_step.
    def visitFor_step(self, ctx:GrammarParser.For_stepContext):
        self.in_bifurcation = True
        self.visitChildren(ctx)
        self.in_bifurcation = False


    # Visit a parse tree produced by GrammarParser#variable_definition.
    def visitVariable_definition(self, ctx:GrammarParser.Variable_definitionContext):
            
        # ? se atribuiu void em variavel
        for i in range(len(ctx.array())):
            tyype = ctx.tyype().getText()
            name = ctx.array(i).identifier().getText()
            array = [self.inside_what_function]
            values = []
            
            if self.ids_defined.get(name): #se existe o array
                if self.ids_defined.get(name)[2]: #se existe outro array c esse nome em outras funcoes
                    array = self.ids_defined.get(name)[2]
                    array.append(self.inside_what_function)

            if(ctx.array_literal()):                
                for k in range(len(ctx.array_literal(i).expression())):

                    ignore, return_value = self.visit(ctx.array_literal(i).expression(k))
                    values.append(return_value)
                        
                    if(ctx.tyype().getText() == Type.INT):
                        token = ctx.array(i).identifier().IDENTIFIER().getPayload()
                        
                        if(ctx.array_literal(i).expression(k).floating()):
                            print("WARNING: possible loss of information initializing float expression to int array \'{}\' at index {} of array literal in line {} and column {}".format(str(ctx.array(i).identifier().getText()), str(k), str(token.line),str(token.column)))
                    
                        if(ctx.array_literal(i).expression(k).string()):
                            print("ERROR: trying to initialize 'char *' expression to 'int' array \'{}\' at index {} of array literal in line {} and column {}".format(str(ctx.array(i).identifier().getText()), str(k), str(token.line),str(token.column)))
        
            # ? coloca os valores do array direitinho
            self.ids_defined[name] = tyype, values, array # ? 0 -> tyype ; 1 -> params ; 2 -> funções q ela pertence


        for i in range(len(ctx.expression())):
            tyype = ctx.tyype().getText()
            name = ctx.identifier(i).getText()
            array = [self.inside_what_function]
            
            if self.ids_defined.get(name): #se existe a variavel
                if self.ids_defined.get(name)[2]: #se existe algo no array de funcoes q ela pertence
                    array = self.ids_defined.get(name)[2]
                    array.append(self.inside_what_function)
            self.ids_defined[name] = tyype, None, array # ? 0 -> tyype ; 1 -> valor ; 2 -> funções q ela pertence

            f.write('\t%' + name + ' = alloca ' + llvm_type(tyype) + ', align 4\n')
            
            if(ctx.expression(i).string()):
                if(tyype != Type.STRING):
                    token = ctx.identifier(i).IDENTIFIER().getPayload()
                    print('ERROR: trying to assign \'char *\' expression to variable \'{}\' in line {} and column {}'.format(str(name),str(token.line),str(token.column)))

            if(ctx.expression(i).function_call()):
                # ? se ele chama uma funcao nessa expressao
                # %1 = call float @ResDiv(float 0x4079000000000000, float 0x4072c00000000000)
                func_type, params, ignore = self.ids_defined.get(ctx.expression(i).function_call().identifier().getText())
                self.param_number = self.param_number + 1
                f.write('\t%' + str(self.param_number) + ' = call ' + llvm_type(func_type) + ' @' + ctx.expression(i).function_call().identifier().getText() + '(')

                for j in range(len(params)):
                    param_name = ctx.expression(i).function_call().expression(j).getText()
                    ignore, param_value, ignore = self.ids_defined.get(param_name)
                    if j: f.write(', ')
                    f.write(llvm_type(params[j][0]) + ' ' + float_to_hex(param_value)) #hex de param_value

                f.write(')\n')

                f.write('\tstore ' + llvm_type(func_type) + ' %' + str(self.param_number) + ', ' + llvm_type(tyype) + '* %' + name + ', align 4\n')

                if(self.ids_defined[ctx.expression(i).function_call().identifier().getText()][0] == Type.VOID):
                    token = ctx.identifier(i).IDENTIFIER().getPayload()
                    print('ERROR: trying to assign \'void\' expression to variable \'{}\' in line {} and column {}'.format(str(ctx.identifier(i).getText()),str(token.line),str(token.column)))
        
        # ? se atribui string p int ou float
        # ? se existe float para int
        if(ctx.tyype().INT() and ctx.expression()):
            # ? busca se existe expressão float
            for i in range(len(ctx.expression())):
                self.dont_print = True
                return_type, return_value, ignore = self.visitExpression(ctx.expression(i))
                self.dont_print = False
                if(self.in_bifurcation): return_value = None

                name = ctx.identifier(i).getText()
                
                if(ctx.identifier()):
                    for identifier in ctx.identifier():
                        if(self.inside_what_function!=""):
                            self.ids_defined[name] = self.ids_defined.get(name)[0], return_value, self.ids_defined.get(name)[2] # ? 0 -> tyype ; 1 -> valor ; 2 -> funções q ela pertence
                        else:  
                            self.ids_defined[name] = self.ids_defined.get(name)[0], None, self.ids_defined.get(name)[2] # ? 0 -> tyype ; 1 -> valor ; 2 -> funções q ela pertence

                # ? armazena a variável

                if(return_type == Type.FLOAT):
                    token = ctx.identifier(i).IDENTIFIER().getPayload()
                    print('WARNING: possible loss of information assigning float expression to int variable \'{}\' in line {} and column {}'.format(str(ctx.identifier(i).getText()),str(token.line),str(token.column)))
        
                if ctx.expression(i).identifier(): f.write('\tstore ' + llvm_type(return_type) + ' %' + str([*self.exists_used_regs(ctx.expression(i).getText())][0]) + ', ' + llvm_type(return_type) + '* ' + '%' + name + ', align 4\n')
                elif ctx.expression(i).integer(): f.write('\tstore ' + llvm_type(return_type) + ' ' + str(return_value) + ', ' + llvm_type(return_type) + '* ' + '%' + str(ctx.identifier(i).getText()) + ', align 4\n')
               

                # ? se return_value for none, colocamos a expressão
                if(return_value == None):
                    self.ids_defined[name] = self.ids_defined.get(name)[0], ctx.expression(i).getText(), self.ids_defined.get(name)[2]

        # ? para acessar o valor de float
        elif(ctx.tyype().FLOAT() and ctx.expression()):
            for i in range(len(ctx.expression())):
                self.dont_print = True
                return_type, return_value, ignore = self.visitExpression(ctx.expression(i))
                self.dont_print = False

                name = ctx.identifier(i).getText()
                # ? armazena a variável
                self.ids_defined[name] = self.ids_defined.get(name)[0], return_value, self.ids_defined.get(name)[2] # ? 0 -> tyype ; 1 -> valor/expressao ; 2 -> funções q ela pertence

                # ? verifica se a variável ou expressão está armazenada num registrador numérico
                #def exists_used_regs(self, var_expr): #{numero reg: (tipo, variavel/expressao)} [*left_reg][0]
                if self.exists_used_regs(ctx.expression(i).getText()):
                    if ctx.expression(i).identifier: f.write('\tstore ' + llvm_type(return_type) + ' %' + str([*self.exists_used_regs(ctx.expression(i).getText())][0]) + ', ' + llvm_type(return_type) + '* ' + '%' + name + ', align 4\n')
                #TODO terminar
              
               
                # ? se return_value for none, colocamos a expressão
                if(return_value == None):
                    self.ids_defined[name] = self.ids_defined.get(name)[0], ctx.expression(i).getText(), self.ids_defined.get(name)[2]
                elif(ctx.expression(i).floating):
                    f.write('\tstore ' + llvm_type(return_type) + ' ' + float_to_hex(return_value) + ', ' + llvm_type(return_type) + '* ' + '%' + str(ctx.identifier(i).getText()) + ', align 4\n')
                
        # return self.visitChildren(ctx)


    def is_in_local_scope(self,func_param,identifier):
        # ? checa se ta nos parametros ou declarado na funcao
        for i in range(len(func_param)):
            if(func_param[i][1] == identifier):
                return True
        
        if self.ids_defined.get(identifier):
            if self.inside_what_function in self.ids_defined.get(identifier)[2]:
                return True
        return False


    # ? pega o tipo da função, buscando se ela tá nos params da função e em ids_defined, verificando se ela pertence a função atual
    def get_local_var_type(self,variable):
        # ? procura nos params da função
        if self.ids_defined.get(self.inside_what_function):
            array = self.ids_defined.get(self.inside_what_function)[1] # * lista de parametros
            for i in range(len(array)):
                if variable == array[i][1]:
                    return array[i][0]
        
        # ? procura no ids_defined
        if self.ids_defined.get(variable):
            array = self.ids_defined.get(variable)[2] # * lista de variaveis a qual ela pertence
            if array:
                if self.inside_what_function in array:
                    return self.ids_defined.get(variable)[0]
        return Type.VOID


    # Visit a parse tree produced by GrammarParser#variable_assignment.
    def visitVariable_assignment(self, ctx:GrammarParser.Variable_assignmentContext):
        # ? se tem variável não definida
        if(ctx.identifier()):
            if(not self.is_in_local_scope(self.ids_defined.get(self.inside_what_function)[1],ctx.identifier().getText())):
                token = ctx.identifier().IDENTIFIER().getPayload()
                print('ERROR: undefined variable \'{}\' in line {} and column {}'.format(str(ctx.identifier().getText()),str(token.line),str(token.column)))
            else:
        # ? se atribui float p int, ou string em int ou float
                if ctx.expression():
                    if(ctx.expression().array()):
                        if(not self.is_in_local_scope(self.ids_defined.get(self.inside_what_function)[1],ctx.expression().array().identifier().getText())):
                            token = ctx.expression().array().identifier().IDENTIFIER().getPayload()
                            print("ERROR: undefined array '{}' in line {} and column {}".format(str(ctx.expression().array().identifier().getText()),str(token.line),str(token.column)))
                            
                        if(ctx.expression().array().expression().floating()):
                            token = ctx.expression().array().identifier().IDENTIFIER().getPayload()
                            print("ERROR: array expression must be an integer, but it is float in line 50 and column 5".format(str(token.line),str(token.column)))
                    
                    expr_type, return_value, ignore = self.visitExpression(ctx.expression())
                    if(self.in_bifurcation): return_value = None

                    name = ctx.identifier().getText()
                
                    # ? armazena a variável
                    if(self.ids_defined.get(name)): self.ids_defined[name] = self.ids_defined.get(name)[0], return_value, self.ids_defined.get(name)[2] # ? 0 -> tyype ; 1 -> valor ; 2 -> funções q ela pertence
                    
                    if(expr_type == Type.FLOAT and self.get_local_var_type(ctx.identifier().getText()) == Type.INT):
                        token = ctx.identifier().IDENTIFIER().getPayload()
                        print('WARNING: possible loss of information assigning float expression to int variable \'{}\' in line {} and column {}'.format(str(ctx.identifier().getText()),str(token.line),str(token.column)))
                    
                    if(expr_type == Type.STRING and self.get_local_var_type(ctx.identifier().getText()) != Type.STRING):
                        token = ctx.identifier().IDENTIFIER().getPayload()
                        print("ERROR: trying to assign 'char *' expression to variable \'{}\' in line {} and column {}".format(str(ctx.identifier().getText()),str(token.line),str(token.column)))

    # Visit a parse tree produced by GrammarParser#expression.
    def visitExpression(self, ctx:GrammarParser.ExpressionContext):
        # print(ctx.getText(), '<<<<<<<<<<<<<<<<<<<<<<<<') #DEBUG
        # ? verifica se existe operação com tipo void
        for i in range(len(ctx.expression())): #num = 2 + 3 -> 2 expressoes, 2 e 3
            if(ctx.expression(i).function_call()):
                if(self.ids_defined[ctx.expression(i).function_call().identifier().getText()][0] == Type.VOID):
                    token = ctx.OP
                    print('ERROR: binary operator \'{}\' used on type void in line {} and column {}'.format(str(ctx.OP.text),str(token.line),str(token.column)))

        return_type = Type.VOID
        return_var = None
        return_name = None
        # ? não tem expr em expr
        if len(ctx.expression()) == 0:
            if ctx.integer():
                return_type = Type.INT
                return_var = int(ctx.integer().getText())
                # return_name = return_var
            elif ctx.floating():
                return_type = Type.FLOAT
                return_var = float(ctx.floating().getText())
            elif ctx.string():
                return_type = Type.STRING
            elif ctx.function_call():
                return_type = self.visit(ctx.function_call())
                return_name = ctx.function_call().identifier().getText()
                params = self.ids_defined.get(ctx.function_call().identifier().getText())[1] # ? (tipo, nome, nome registrador de variável)
                
                # print(params, 'a<<<<<<<<<') #DEBUG
                if not self.dont_print:
                    f.write('\tcall ' + llvm_type(return_type) + ' @' + return_name + '(')
                    # print(params, '<<<<<<<<<<<<<<<') #DEBUG
                    for i in range(len(params)):
                        # print(ctx.function_call().expression(i).getText(), '<<<<<<<<<') #DEBUG
                        value = 0 #TODO pegar valor se for identifier
                        if self.ids_defined.get(ctx.function_call().expression(i).getText()):
                            ignore, value, ignore = self.ids_defined.get(ctx.function_call().expression(i).getText())

                        if i != 0: f.write(', ')
                        if type(value) == float:
                            f.write(llvm_type(params[i][0]) + ' ' + float_to_hex(value))
                        else:
                            f.write(llvm_type(params[i][0]) + ' ' + str(value))
                        
                    f.write(')\n')

            elif ctx.identifier():
                if (self.ids_defined.get(ctx.identifier().getText()) != None):
                    return_type = self.ids_defined.get(ctx.identifier().getText())[0]
                    return_var = self.ids_defined.get(ctx.identifier().getText())[1]
                    return_name = ctx.identifier().getText()
                    # print('estou passando pelo ctx.identifier em',self.inside_what_function) #DEBUG
                elif (self.ids_defined.get(self.inside_what_function)[1] != None):
                    array = self.ids_defined.get(self.inside_what_function)[1]
                    for i in range(len(array)):
                        if(array[i][1] == ctx.identifier().getText()):
                            return_type = array[i][0]
                            return_name = array[i][1]
                            
                else: return_type = Type.VOID
            elif ctx.array():
                if self.ids_defined.get(ctx.array().identifier().getText()):
                    return_type = self.ids_defined.get(ctx.array().identifier().getText())[0]
                    ignore, return_var = self.visit(ctx.array())
        # ? tem uma expr nela
        elif len(ctx.expression()) == 1:
            if ctx.OP:
                #TODO modificar o return name aq tb?
                return_type, return_var, return_name = self.visit(ctx.expression(0))
                if(ctx.OP.text == '-' and return_var):
                    print('line {} Expression - {} simplified to: {}'.format(str(ctx.OP.line),str(return_var),str(-return_var)))
                    return_var = -return_var
            else:
                # print('visitando1', ctx.expression(0).getText(),'<<<<<<<<<') #DEBUG
                return_type, return_var, ignore = self.visit(ctx.expression(0))
                return_name = ctx.expression(0).getText()
        # ? tem duas expr nela
        elif len(ctx.expression()) == 2:
            # print(ctx.getText(),'expressao <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<') #DEBUG

            left,left_value, left_name = self.visit(ctx.expression(0))
            # print('visitando expressao',ctx.expression(1).getText()) #DEBUG
            right,right_value, right_name = self.visit(ctx.expression(1))

            # ? verificacao de tipo
            if(left == Type.STRING or right == Type.STRING): return_type = Type.STRING
            elif(left == Type.FLOAT or right == Type.FLOAT): return_type = Type.FLOAT
            elif(left == Type.INT or right == Type.INT): return_type = Type.INT

            # ? verificacao de valores
            token = ctx.OP
            output = 'line {} Expression {} {} {} simplified to: {}'
            if(left_value != None and right_value != None):
                if(ctx.OP.text == '*' or ctx.OP.text == '/'):
                    if(ctx.OP.text == '*'):
                        print(output.format(str(token.line),str(left_value),ctx.OP.text,str(right_value),str(left_value*right_value)))
                        
                        return_var = left_value * right_value
                    else:
                        print(output.format(str(token.line),str(left_value),ctx.OP.text,str(right_value),str(left_value/right_value)))
                        
                        return_var = left_value / right_value
                elif(ctx.OP.text == '+' or ctx.OP.text == '-'):
                    if(ctx.OP.text == '+'):
                        print(output.format(str(token.line),str(left_value),ctx.OP.text,str(right_value),str(left_value+right_value)))
                        
                        return_var = left_value + right_value

                    else:
                        print(output.format(str(token.line),str(left_value),ctx.OP.text,str(right_value),str(left_value-right_value)))
                        
                        return_var = left_value - right_value
                else:
                    # * converte left e right em string, concatena c o OP e dá eval
                    return_var = int(eval(str(left_value)+ctx.OP.text+str(right_value)))
                    print(output.format(str(token.line),str(left_value),ctx.OP.text,str(right_value),str(return_var)))

            # ? verificação se a expressão tá num parâmetro. se tiver, faz diferente :)
            if(not self.in_return_function_check):
                if(ctx.OP.text == '*' or ctx.OP.text == '/'):
                    if(ctx.OP.text == '*'):
                        if left_name == right_name: # ? operacao com mesmo nome
                            #TODO fazer verificação feita depois
                            # atribui valor a um registrador numerico para receber o valor do registrador variavel
                            if( left_name != None ):
                                left_reg = self.exists_used_regs(left_name) #{numero reg: (tipo, variavel/expressao)}
                                if left_reg == None:
                                    self.param_number = self.param_number + 1
                                    f.write('\t%' + str(self.param_number) + ' = load ' + llvm_type(left) + ', ' + llvm_type(left) + '* %' + left_name + ', align 4\n')
                                    self.used_regs[self.param_number] = (left, '%'+left_name) # ? tipo, reg var associado ou expressao associada
                                    left_reg = {self.param_number: (left, '%'+left_name)}
                                    # print('alocando',left_reg) #DEBUG

                                # atribui a um registrador a multiplicação
                                self.param_number = self.param_number + 1
                                f.write('\t%' + str(self.param_number) + ' = mul ' + llvm_type(left) + ' %' + str([*left_reg][0]) + ', %' + str([*left_reg][0]) + '\n')

                                self.used_regs[self.param_number] = (left, ctx.getText()) # ? tipo, reg var associado ou expressao associada

                                # ! isso aqui é usado no 00.c na função square, se for modificar, se atente para o output discrepante

                    else:
                        if left_name == right_name:
                            pass
                        else:
                            
                            if( left_name != None ):
                                # print('estou crashando tentando achar',left_name) #DEBUG
                                left_reg = self.exists_used_regs(left_name) #{numero reg: (tipo, variavel/expressao)}
                                if left_reg == None:
                                    self.param_number = self.param_number + 1
                                    f.write('\t%' + str(self.param_number) + ' = load ' + llvm_type(left) + ', ' + llvm_type(left) + '* %' + left_name + ', align 4\n')
                                    self.used_regs[self.param_number] = (left, '%'+left_name) # ? tipo, reg var associado ou expressao associada
                                    left_reg = {self.param_number: (left, left_name)}


                            if(right_name != None):
                                right_reg = self.exists_used_regs(right_name)
                                if right_reg == None:
                                    self.param_number = self.param_number + 1
                                    f.write('\t%' + str(self.param_number) + ' = load ' + llvm_type(right) + ', ' + llvm_type(right) + '* %' + right_name + ', align 4\n')
                                    self.used_regs[self.param_number] = (right, '%'+right_name) # ? tipo, reg var associado ou expressao associada
                                    right_reg = {self.param_number: (right, right_name)}

                            if(left_name != None and right_name != None):
                                # atribui a um registrador a multiplicação
                                self.param_number = self.param_number + 1
                                f.write('\t%' + str(self.param_number) + ' = fdiv ' + llvm_type(left) + ' %' + str([*left_reg][0]) + ', %' + str([*right_reg][0]) + '\n')

                                self.used_regs[self.param_number] = (left, ctx.getText()) # ? tipo, reg var associado ou expressao associada
                elif(ctx.OP.text == '+' or ctx.OP.text == '-'):
                    if(ctx.OP.text == '+'):
                        if left_name == right_name:
                            pass
                        else:
                            # print(ctx.getText(), '<<<<<<<<<<<<<<<<<<<<<') #DEBUG
                            if(left_name != None):
                                left_reg = self.exists_used_regs(left_name) #{numero reg: (tipo, variavel/expressao)}
                                if left_reg == None:
                                    self.param_number = self.param_number + 1
                                    f.write('\t%' + str(self.param_number) + ' = load ' + llvm_type(left) + ', ' + llvm_type(left) + '* %' + left_name + ', align 4\n')
                                    self.used_regs[self.param_number] = (left, '%'+left_name) # ? tipo, reg var associado ou expressao associada
                                    left_reg = {self.param_number: (left, '%'+left_name)}
                                    # print('alocando',left_reg) #DEBUG

                            if(right_name != None):
                                right_reg = self.exists_used_regs(right_name)
                                # print(right_reg,'<<<<<<<<<<') #DEBUG
                                if right_reg == None:
                                    self.param_number = self.param_number + 1
                                    f.write('\t%' + str(self.param_number) + ' = load ' + llvm_type(right) + ', ' + llvm_type(right) + '* %' + right_name + ', align 4\n')
                                    self.used_regs[self.param_number] = (right, '%'+right_name) # ? tipo, reg var associado ou expressao associada
                                    right_reg = {self.param_number: (right, '%'+right_name)}
                                    # print('alocando',right_reg) #DEBUG

                            if(left_name != None and right_name != None):
                                # atribui a um registrador a multiplicação
                                self.param_number = self.param_number + 1
                                f.write('\t%' + str(self.param_number) + ' = fadd ' + llvm_type(left) + ' %' + str([*left_reg][0]) + ', %' + str([*right_reg][0]) + '\n')

                                self.used_regs[self.param_number] = (left, ctx.getText()) # ? tipo, reg var associado ou expressao associada
                            else:
                                print('left_value = ',left_value) #DEBUG
                                print('right_value = ',right_value) #DEBUG
                                return_var = left_value + right_value # !

                    else:
                        pass
                else:
                    pass

        return return_type, return_var, return_name

    # ? verifica se a variável ou expressão está armazenada num registrador numérico
    def exists_used_regs(self, var_expr):
        return_reg = None
        # if var_expr == None: return None # ! Bug fix
        # print('var_expr é',var_expr) #DEBUG
        for i, reg in enumerate(self.used_regs):
            temp = self.used_regs.get(reg)
            # print('comparando o que quero {} com o que tenho {}'.format(str(var_expr),str(temp[1]))) #DEBUG
            if temp[1] == '%'+var_expr:
                # print('achei') #DEBUG
                return_reg = {reg: temp}
                break
            if temp[1] == '('+var_expr+')':
                # print('achei') #DEBUG
                return_reg = {reg: temp}
                break
            if temp[1] == var_expr:
                # print('achei') #DEBUG
                return_reg = {reg: temp}
                break

        return return_reg

    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):
        # print(self.ids_defined.get(ctx.identifier().getText()),'<<<<<<<<<<<<<<<<') #DEBUG
        ignore, index = self.visit(ctx.expression())
        # print('index',index) #DEBUG
        return_var = self.ids_defined.get(ctx.identifier().getText())[1][index]
        return 0, return_var


    # Visit a parse tree produced by GrammarParser#array_literal.
    def visitArray_literal(self, ctx:GrammarParser.Array_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#function_call.
    def visitFunction_call(self, ctx:GrammarParser.Function_callContext):
        # ? verifica o numero de parametros
        name = ctx.identifier().getText()  
        if(len(self.ids_defined[name][1]) != len(ctx.expression())):
            token = ctx.identifier().IDENTIFIER().getPayload()
            print('ERROR: incorrect number of parameters for function \'{}\' in line {}, and column {}. Expecting {}, but {} were given'.format(str(name), str(token.line), str(token.column), str(len(self.ids_defined[name][1])), str(len(ctx.expression()))))
        # ? verifica se pode perder informaçao passando float como inteiro
        elif ctx.expression():
            # * cada expression é um parametro
            for i in range(len(ctx.expression())):
                self.in_return_check = True
                expr_type = self.visitExpression(ctx.expression(i))
                self.in_return_check = False
                name = ctx.expression(i).getText()
                # * busca o tipo esperado na declaracao da funcao
                array = self.ids_defined.get(ctx.identifier().getText())[1]
                param_type = array[i][0]
                if(expr_type == Type.FLOAT and param_type == Type.INT):
                    token = ctx.identifier().IDENTIFIER().getPayload()
                    print('WARNING: possible loss of information converting float expression to int expression in parameter {} of function \'{}\' in line {} and column {}'.format(str(i),str(ctx.identifier().getText()),str(token.line),str(token.column)))
        return self.ids_defined.get(ctx.identifier().getText())[0]


    # Visit a parse tree produced by GrammarParser#arguments.
    def visitArguments(self, ctx:GrammarParser.ArgumentsContext):
        arguments = []
        for i in range(len(ctx.tyype())):
            tyype = ctx.tyype(i).getText()
            name = ctx.identifier(i).getText()
            arguments.append((tyype, name, '%'+str(i))) # ? inclui a referência dele como parâmetro
            if(i != 0): f.write(', ')
            f.write(llvm_type(tyype)+' %'+str(i))
        return arguments 


    # Visit a parse tree produced by GrammarParser#tyype.
    def visitTyype(self, ctx:GrammarParser.TyypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#integer.
    def visitInteger(self, ctx:GrammarParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#floating.
    def visitFloating(self, ctx:GrammarParser.FloatingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#string.
    def visitString(self, ctx:GrammarParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#identifier.
    def visitIdentifier(self, ctx:GrammarParser.IdentifierContext):
        return self.visitChildren(ctx)