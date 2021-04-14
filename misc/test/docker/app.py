from os import environ

for key, value in dict(environ).items():
    print(f'{key}: {value}')
