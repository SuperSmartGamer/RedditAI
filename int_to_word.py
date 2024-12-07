import re

def number_to_words_in_text(text):
    def number_to_words(num):
        if num == 0:
            return "zero"

        def below_20(n):
            words = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
            return words[n]

        def tens(n):
            words = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            return words[n]

        def convert(n):
            if n == 0:
                return ""
            elif n < 20:
                return below_20(n)
            elif n < 100:
                return tens(n // 10) + (" " + below_20(n % 10) if n % 10 != 0 else "")
            elif n < 1000:
                return below_20(n // 100) + " hundred" + (" " + convert(n % 100) if n % 100 != 0 else "")
            else:
                powers = [
                    (10**18, "quintillion"), (10**15, "quadrillion"), (10**12, "trillion"), 
                    (10**9, "billion"), (10**6, "million"), (10**3, "thousand")
                ]
                for power, name in powers:
                    if n >= power:
                        return convert(n // power) + " " + name + (" " + convert(n % power) if n % power != 0 else "")

        return convert(num).strip()

    # Use regular expressions to find all numbers in the text
    def replace_number(match):
        number = int(match.group())
        return number_to_words(number)

    return re.sub(r'\d+', replace_number, text)

# Example usage
