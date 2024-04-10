#I love you, China.
#I evol uoy, anihC.
def reverse(s):
    res = ''
    symbol = '.,'
    for i in s.split(' '):
        if i[-1] in symbol:
            temp = i[-1]
            res += i[:-1][::-1]
            res += temp
        else:
            res += i[::-1]
        res += ' '
    return res





def main():
    print(reverse('I love you, China.'))

main()
