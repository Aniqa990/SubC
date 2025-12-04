func int add(int a, int b) {
    return a + b;
}

func float average(int a, float b) {
    float result = (a + b) / 2;   // mix int + float → float
    return result;
}

func bool isPositive(float x) {
    if (x > 0) {
        return true;
    } else {
        return false;
    }
}

func int main() {
    int x = 10;
    float y = 3.5;

    // test function calls
    int sum = add(x, 5);
    float avg = average(sum, y);

    // boolean logic test
    bool pos = isPositive(avg);

    // new scope test
    if (1){
        int z = 100;
        print(z);
    }

    // z should be out of scope here
    print(z);  // uncomment to test scope error

    print(x);
    print(sum);
    print(avg);
    print(pos);

    return 0;
}