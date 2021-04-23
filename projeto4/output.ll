define i32 @square(i32 %0) {
	%x = alloca i32, align 4
	store i32 %0, i32* %x, align 4
	%2 = load i32, i32* %x, align 4
	%3 = mul i32 %2, %2
	ret i32 %3
}

define void @splash(i32 %0) {
	%k = alloca i32, align 4
	store i32 %0, i32* %k, align 4
	ret void
}

