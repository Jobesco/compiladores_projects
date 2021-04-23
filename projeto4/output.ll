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

define float @ResDiv(float %0, float %1) {
	%k1 = alloca float, align 4
	store float %0, float* %k1, align 4
	%k2 = alloca float, align 4
	store float %1, float* %k2, align 4
}

