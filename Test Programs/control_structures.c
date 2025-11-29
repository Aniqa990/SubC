func int main() {
    int i = 0;
    int s = 0;
    for (int i = 0; i < 5; i = i + 1) {
        s = s + i;
    }
    if (s > 5) {
        print(s);
    } else {
        print(0);
    }
    while (i < 3) {
        i = i + 1;
    }
    return 0;
}
