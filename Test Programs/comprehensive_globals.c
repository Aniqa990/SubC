int total = 0;
float average = 0.0;

func void addValue(int val) {
    total = total + val;
}

func int getValue() {
    return total;
}

func int main() {
    int x = 10;
    int y = 20;
    
    addValue(x);
    addValue(y);
    
    int result = getValue();
    if (result > 20) {
        print(result);
    }
    
    return result;
}
