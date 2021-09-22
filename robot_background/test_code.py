s = b'sjsghjshg'
s.
t = s.find(b'\n')
if t:
    print(s[:t+1])
    print(s[t+1:])