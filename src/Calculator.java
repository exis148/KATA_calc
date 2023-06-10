import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class Calculator {




    public static void main(String[] args)

    {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Введите выражение: ");
        String expression = scanner.nextLine();
        try {
            String result = calculate(expression);
            System.out.println("Результат: " + result);
        } catch (IllegalArgumentException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
    }

    public static String calculate(String expression) {
        String[] parts = expression.split("\\s+");

        if (parts.length != 3) {
            throw new IllegalArgumentException("Некорректное выражение");
        }

        String operand1 = parts[0];
        String operator = parts[1];
        String operand2 = parts[2];

        if (!(isArabicNumber(operand1) && isArabicNumber(operand2)) && !(isRomanNumber(operand1) && isRomanNumber(operand2)))

        {
            throw new IllegalArgumentException("Калькулятор может работать только с арабскими или римскими цифрами одновременно");
        }

        int num1, num2;
        boolean isRoman = false;


        if (isArabicNumber(operand1))
        {
            num1 = Integer.parseInt(operand1);
            num2 = Integer.parseInt(operand2);
            if (num1 < 1 || num1 > 10 || num2 < 1 || num2 > 10) {

                throw new IllegalArgumentException("Введены неподходящие числа. Калькулятор принимает числа от 1 до 10 включительно.");
            }
        } else {

            num1 = romanToArabic.get(operand1);
            num2 = romanToArabic.get(operand2);
            isRoman = true;


        }

        int result;
        if (operator.equals("+")) {
            result = num1 + num2;
        } else if (operator.equals("-")) {
            result = num1 - num2;
        } else if (operator.equals("*")) {
            result = num1 * num2;
        } else if (operator.equals("/")) {
            if (num2 == 0) {
                throw new IllegalArgumentException("Деление на ноль недопустимо");
            }
            result = num1 / num2;
        } else {
            throw new IllegalArgumentException("Неподдерживаемая операция. Поддерживаются только +, -, * и /");
        }

        if (isRoman) {
            if (result <= 0) {
                throw new IllegalArgumentException("Результатом работы калькулятора с римскими числами могут быть только положительные числа");
            }
            return arabicToRoman.get(result);
        } else {
            return String.valueOf(result);
        }
    }

    private static boolean isArabicNumber(String input) {
        try {
            Integer.parseInt(input);
            return true;
        } catch (NumberFormatException e) {


            return false;
        }
    }

    private static boolean isRomanNumber(String input) {
        return romanToArabic.containsKey(input);
    }
    private static final Map<String, Integer> romanToArabic = new HashMap<>();

    static {

        romanToArabic.put("I", 1);
        romanToArabic.put("II", 2);
        romanToArabic.put("III", 3);
        romanToArabic.put("IV", 4);
        romanToArabic.put("V", 5);
        romanToArabic.put("VI", 6);
        romanToArabic.put("VII", 7);
        romanToArabic.put("VIII", 8);
        romanToArabic.put("IX", 9);
        romanToArabic.put("X", 10);
    }

    private static final Map<Integer, String> arabicToRoman = new HashMap<>();

    static {


        arabicToRoman.put(1, "I");
        arabicToRoman.put(2, "II");
        arabicToRoman.put(3, "III");
        arabicToRoman.put(4, "IV");
        arabicToRoman.put(5, "V");
        arabicToRoman.put(6, "VI");
        arabicToRoman.put(7, "VII");
        arabicToRoman.put(8, "VIII");
        arabicToRoman.put(9, "IX");
        arabicToRoman.put(10, "X");
    }
}