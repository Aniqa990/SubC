func int add(int a, int b) {
    return a + b;
}

func int main() {
    int x = 5;
    float y;

    y = x + true;        // Error: type mismatch (int + bool)
    int x = 10;          // Error: redeclaration in the same scope
    z = 3;               // Error: 'z' undeclared

    int result = add(2); // Error: missing argument for 'add' function

    if (x) {             // Error: 'if' condition must be bool
        print("Hello");
    }

    return 0;
}
