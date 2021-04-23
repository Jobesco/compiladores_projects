define i32 @square(i32 %0) {
	%x = alloca i32, align 4
	store i32 %0, i32* %x, align 4
	%2 = load i32, i32* %x, align 4
	%3 = mul i32 %2, %2
}

