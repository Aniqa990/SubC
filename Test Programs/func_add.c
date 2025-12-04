// func int add(int a, int b) {
// 	return a + b;
// }

// func int main() {
// 	int x = 5;
// 	int y = add(2, 3);
// 	print(x);
// 	print(y);
// 	return 0;
// }

// Simple SubC test program

func int add(int a, int b) {
    return a + b;
}

func int multiply(int x, int y) {
    int result = x * y;
    return result;
}

func int main() {
    int x = 5;
    int y = 10;
    int sum = add(x, y);
    int product = multiply(sum, 2);

    if (product > 50) {
        print(product);
    } else {
        print(0);
    }

    return 0;
}
