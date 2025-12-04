int count = 100;
bool debug = false;

func int add(int a, int b) {
    return a + b;
}

func int main() {
    int result = add(10, 20);
    if (result > count) {
        print(result);
    }
    return result;
}
