# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GrammarParser import GrammarParser
else:
    from GrammarParser import GrammarParser

# This class defines a complete generic visitor for a parse tree produced by GrammarParser.

'''
COMO RESGATAR INFORMAÇÕES DA ÁRVORE

Observe o seu Grammar.g4. Cada regra sintática gera uma função com o nome corespondente no Visitor e na ordem em que está na gramática.

Se for utilizar sua gramática do projeto 1, por causa de conflitos com Python, substitua as regras file por fiile e type por tyype. Use prints temporários para ver se está no caminho certo.  
"make tree" agora desenha a árvore sintática, se quiser vê-la para qualquer input, enquanto "make" roda este visitor sobre o a árvore gerada a partir de Grammar.g4 alimentada pelo input.

Exemplos:

# Obs.: Os exemplos abaixo utilizam nós 'expression', mas servem apra qualquer tipo de nó

self.visitChildren(ctx) # visita todos os filhos do nó atual
expr = self.visit(ctx.expression())  # visita a subárvore do nó expression e retorna o valor retornado na função "visitRegra"

for i in range(len(ctx.expression())): # para cada expressão que este nó possui...
    ident = ctx.expression(i) # ...pegue a i-ésima expressão


if ctx.FLOAT() != None: # se houver um FLOAT (em vez de INT ou VOID) neste nó (parser)
    return Type.FLOAT # retorne tipo float

ctx.identifier().getText()  # Obtém o texto contido no nó (neste caso, será obtido o nome do identifier)

token = ctx.identifier(i).IDENTIFIER().getPayload() # Obtém o token referente à uma determinada regra léxica (neste caso, IDENTIFIER)
token.line      # variável com a linha do token
token.column    # variável com a coluna do token
'''


# Dica: Retorne Type.INT, Type.FLOAT, etc. Nos nós e subnós das expressões para fazer a checagem de tipos enquanto percorre a expressão.
class Type:
    VOID = "void"
    INT = "int"
    FLOAT = "float"
    STRING = "char *"

class GrammarCheckerVisitor(ParseTreeVisitor):
    ids_defined = {} # Dicionário para armazenar as informações necessárias para cada identifier definido
    inside_what_function = "" # String que guarda a função atual que o visitor está visitando. Útil para acessar dados da função durante a visitação da árvore sintática da função.

    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx:GrammarParser.FiileContext):
        return self.visitChildren(ctx)


     # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx:GrammarParser.Function_definitionContext):
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()
        params = self.visit(ctx.arguments())
        self.ids_defined[name] = tyype, params, None # ? 0 -> tyype ; 1 -> params
        self.inside_what_function = name
        self.visit(ctx.body())
        return


    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx:GrammarParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx:GrammarParser.StatementContext):
        self.visitChildren(ctx)
        if(ctx.RETURN()):
            if(ctx.expression().function_call()):
                 # ? verifica se a expressão retornada é void
                if(self.ids_defined[ctx.expression().function_call().identifier().getText()][0] == Type.VOID):
                    token = ctx.RETURN().getPayload()
                    print('ERROR: trying to return void expression from function \'{}\' in line {} and column {}'.format(str(self.inside_what_function),str(token.line),str(token.column)))
                # ? se a função é float num return de int
                elif(self.ids_defined.get(ctx.expression().function_call().identifier().getText())[0] == Type.FLOAT and self.ids_defined.get(self.inside_what_function)[0] == Type.INT):
                    token = ctx.RETURN().getPayload()
                    print('WARNING: possible loss of information returning float expression from int function \'{}\' in line {} and column {}'.format(self.inside_what_function,str(token.line),str(token.column)))
        # ? se a função void tiver return
        if(ctx.RETURN() and self.ids_defined[self.inside_what_function][0] == Type.VOID):
            token = ctx.RETURN().getPayload() # Obtém o token referente à uma determinada regra léxica (neste caso, IDENTIFIER)
            print("ERROR: trying to return a non void expression from void function \'{}\' in line {} and column {}".format(self.inside_what_function,str(token.line), str(token.column)))


    # Visit a parse tree produced by GrammarParser#if_statement.
    def visitIf_statement(self, ctx:GrammarParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#else_statement.
    def visitElse_statement(self, ctx:GrammarParser.Else_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_loop.
    def visitFor_loop(self, ctx:GrammarParser.For_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_initializer.
    def visitFor_initializer(self, ctx:GrammarParser.For_initializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_condition.
    def visitFor_condition(self, ctx:GrammarParser.For_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_step.
    def visitFor_step(self, ctx:GrammarParser.For_stepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#variable_definition.
    def visitVariable_definition(self, ctx:GrammarParser.Variable_definitionContext):
        # ? se atribuiu void em variavel
        for i in range(len(ctx.array())):
            tyype = ctx.tyype().getText()
            name = ctx.array(i).identifier().getText()
            array = [self.inside_what_function]
            
            if self.ids_defined.get(name): #se existe o array
                if self.ids_defined.get(name)[2]: #se existe outro array c esse nome em outras funcoes
                    array = self.ids_defined.get(name)[2]
                    array.append(self.inside_what_function)
            self.ids_defined[name] = tyype, None, array # ? 0 -> tyype ; 1 -> params ; 2 -> funções q ela pertence

            if(ctx.array_literal()):                
                for k in range(len(ctx.array_literal(i).expression())):                    
                    if(ctx.tyype().getText() == Type.INT):
                        token = ctx.array(i).identifier().IDENTIFIER().getPayload()
                        
                        if(ctx.array_literal(i).expression(k).floating()):
                            print("WARNING: possible loss of information initializing float expression to int array \'{}\' at index {} of array literal in line {} and column {}".format(str(ctx.array(i).identifier().getText()), str(k), str(token.line),str(token.column)))
                    
                        if(ctx.array_literal(i).expression(k).string()):
                            print("ERROR: trying to initialize 'char *' expression to 'int' array \'{}\' at index {} of array literal in line {} and column {}".format(str(ctx.array(i).identifier().getText()), str(k), str(token.line),str(token.column)))
        
        for i in range(len(ctx.expression())):
            tyype = ctx.tyype().getText()
            name = ctx.identifier(i).getText()
            array = [self.inside_what_function]
            
            if self.ids_defined.get(name): #se existe a variavel
                if self.ids_defined.get(name)[2]: #se existe algo no array de variavel
                    array = self.ids_defined.get(name)[2]
                    array.append(self.inside_what_function)
            self.ids_defined[name] = tyype, None, array # ? 0 -> tyype ; 1 -> params ; 2 -> funções q ela pertence
            
            if(ctx.expression(i).string()):
                if(tyype != Type.STRING):
                    token = ctx.identifier(i).IDENTIFIER().getPayload()
                    print('ERROR: trying to assign \'char *\' expression to variable \'{}\' in line {} and column {}'.format(str(name),str(token.line),str(token.column)))

            if(ctx.expression(i).function_call()):
                if(self.ids_defined[ctx.expression(i).function_call().identifier().getText()][0] == Type.VOID):
                    token = ctx.identifier(i).IDENTIFIER().getPayload()
                    print('ERROR: trying to assign \'void\' expression to variable \'{}\' in line {} and column {}'.format(str(ctx.identifier(i).getText()),str(token.line),str(token.column)))
        
        # ? se atribui string p int ou float
        # ? se existe float para int
        if(ctx.tyype().INT() and ctx.expression()):
            # ? busca se existe expressão float
            for i in range(len(ctx.expression())):
                return_type = self.visitExpression(ctx.expression(i))

                if(return_type == Type.FLOAT):
                    token = ctx.identifier(i).IDENTIFIER().getPayload()
                    print('WARNING: possible loss of information assigning float expression to int variable \'{}\' in line {} and column {}'.format(str(ctx.identifier(i).getText()),str(token.line),str(token.column)))

        return self.visitChildren(ctx)


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
                    
                    expr_type = self.visitExpression(ctx.expression())
                    
                    if(expr_type == Type.FLOAT and self.get_local_var_type(ctx.identifier().getText()) == Type.INT):
                        token = ctx.identifier().IDENTIFIER().getPayload()
                        print('WARNING: possible loss of information assigning float expression to int variable \'{}\' in line {} and column {}'.format(str(ctx.identifier().getText()),str(token.line),str(token.column)))
                    
                    if(expr_type == Type.STRING and self.get_local_var_type(ctx.identifier().getText()) != Type.STRING):
                        token = ctx.identifier().IDENTIFIER().getPayload()
                        print("ERROR: trying to assign 'char *' expression to variable \'{}\' in line {} and column {}".format(str(ctx.identifier().getText()),str(token.line),str(token.column)))


    # Visit a parse tree produced by GrammarParser#expression.
    def visitExpression(self, ctx:GrammarParser.ExpressionContext):
        # ? verifica se existe operação com tipo void
        for i in range(len(ctx.expression())): #num = 2 + 3 -> 2 expressoes, 2 e 3
            if(ctx.expression(i).function_call()):
                if(self.ids_defined[ctx.expression(i).function_call().identifier().getText()][0] == Type.VOID):
                    token = ctx.OP
                    print('ERROR: binary operator \'{}\' used on type void in line {} and column {}'.format(str(ctx.OP.text),str(token.line),str(token.column)))

        return_type = Type.VOID
        # ? não tem expr em expr
        if len(ctx.expression()) == 0:
            if ctx.integer():
                return_type = Type.INT
            elif ctx.floating():
                return_type = Type.FLOAT
            elif ctx.string():
                return_type = Type.STRING
            elif ctx.function_call():
                return_type = self.visit(ctx.function_call())
            elif ctx.identifier():
                if (self.ids_defined.get(ctx.identifier().getText()) != None):
                    return_type = self.ids_defined.get(ctx.identifier().getText())[0]
                elif (self.ids_defined.get(self.inside_what_function)[1] != None):
                    array = self.ids_defined.get(self.inside_what_function)[1]
                    for i in range(len(array)):
                        if(array[i][1] == ctx.identifier().getText()):
                            return_type = array[i][0]
                else: return_type = Type.VOID
            elif ctx.array():
                if self.ids_defined.get(ctx.array().identifier().getText()):
                    return_type = self.ids_defined.get(ctx.array().identifier().getText())[0]
        # ? tem uma expr nela
        elif len(ctx.expression()) == 1:
            if ctx.OP:
                return_type = self.visit(ctx.expression(0))
            else:
                return_type = self.visit(ctx.expression(0))
        # ? tem duas expr nela
        elif len(ctx.expression()) == 2:  
            left = self.visit(ctx.expression(0))
            right = self.visit(ctx.expression(1))
            if(left == Type.STRING or right == Type.STRING): return_type = Type.STRING
            elif(left == Type.FLOAT or right == Type.FLOAT): return_type = Type.FLOAT
            elif(left == Type.INT or right == Type.INT): return_type = Type.INT
        return return_type


    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):
        return self.visitChildren(ctx)


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
                expr_type = self.visitExpression(ctx.expression(i))
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
            arguments.append((tyype, name))
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