int global_x = 10;
float global_y = 2.5;

func void increment() {
    global_x = global_x + 1;
}

func int main() {
    print(global_x);
    increment();
    print(global_x);
    return global_x;
}
