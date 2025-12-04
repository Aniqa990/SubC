import lexer

code = """func void test() {
}

func int main() {
    return 0;
}"""

result = lexer.check(code, print_tokens=True)
print("Result:", result)

