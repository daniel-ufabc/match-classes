import unidecode as ud
import functools
import re


tokens_re = {
    'MINUTE': re.compile(r'minutos|minuto|min|m'),
    'HOUR': re.compile(r'horas|hora|hrs|hr|h'),
    'MON': re.compile(r'segundas-feiras|segunda-feira|segundas|segunda|seg'),
    'TUE': re.compile(r'tercas-feiras|terca-feira|tercas|terca|ter'),
    'WED': re.compile(r'quartas-feiras|quarta-feira|quartas|quarta|qua'),
    'THU': re.compile(r'quintas-feiras|quinta-feira|quintas|quinta|qui'),
    'FRI': re.compile(r'sextas-feiras|sexta-feira|sextas|sexta|sex'),
    'SAT': re.compile(r'sabados|sabado|sab'),
    'WEEKLY': re.compile(r'semanalmente|semanais|semanal'),
    'FORTNIGHT': re.compile(r'quinzenalmente|quinzenais|quinzenal'),
    'NUM2': re.compile(r'[0-9][0-9]'),
    'NUM1': re.compile(r'[0-9]'),
    'SPC': re.compile(r'[ \t]+'),
    'SEP': re.compile(r'ate as|ate|as|--|-'),
    'PARITY_I': re.compile(r'i'),
    'PARITY_II': re.compile(r'ii'),
    'COLON': re.compile(r':'),
    'SEMICOLON': re.compile(r';'),
    'COMMA': re.compile(r','),
    'DAS': re.compile(r'desde as|desde|das|de')
}

buffer = None


class Token:
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    HOUR = 7
    MINUTE = 8
    WEEKLY = 9
    FORTNIGHT = 10
    NUM1 = 11
    NUM2 = 12
    SPC = 13
    SEP = 14
    PARITY_I = 15
    PARITY_II = 16
    COLON = 17
    SEMICOLON = 18
    COMMA = 19
    DAS = 20

    def __init__(self, t_type, t_content=None):
        self.type = t_type
        self.content = t_content

    def value(self):
        if self.type == Token.NUM1 or self.type == Token.NUM2:
            return int(self.content)
        return self.content


def memoize(f):
    memo = {}

    @functools.wraps(f)
    def helper(*args):
        # DEBUG: print(f.__name__, *args)
        if buffer not in memo:
            memo[buffer] = {}
        if args not in memo[buffer]:
            memo[buffer][args] = f(*args)
        return memo[buffer][args]

    return helper


@memoize
def token(name, k):
    global buffer

    compiled_re = tokens_re[name]
    match = compiled_re.match(buffer[k:])
    if match:
        return True, k + match.end(), Token(getattr(Token, name), match.group())
    return False, k, None

# define classes


@memoize
def schedule_expr(k):
    """schedule_expr     <- schedule_expr1 schedule_expr2? OPTSPC"""
    success, k1, node1 = schedule_expr1(k)
    if not success:
        return False, k, None
    success, k2, list_of_nodes = schedule_expr2(k1)
    if not success:
        return True, k1, [node1]
    success, k3, _ = optspc(k2)
    return True, k3, [node1] + list_of_nodes


@memoize
def schedule_expr1(k):
    """schedule_expr1    <- OPTSPC schedule_expr3 OPTSPC"""
    success, k1, _ = optspc(k)
    success, k2, node1 = schedule_expr3(k1)
    if not success:
        return False, k, None
    success, k3, _ = optspc(k2)
    return True, k3, node1


@memoize
def schedule_expr2(k):
    """schedule_expr2    <- SEMICOLON schedule_expr1 schedule_expr2? / SEMICOLON"""
    success, k1, _ = token('SEMICOLON', k)
    if not success:
        return False, k, None
    success, k2, node1 = schedule_expr1(k1)
    if not success:
        return True, k1, []
    success, k3, list_of_nodes = schedule_expr2(k2)
    if not success:
        return True, k2, [node1]
    return True, k3, [node1] + list_of_nodes


@memoize
def schedule_expr3(k):
    """schedule_expr3    <- session_expr LINK1 repeat_expr / session_expr"""
    success, k1, node1 = session_expr(k)
    if not success:
        return False, k, None
    success, k2, _ = link1(k1)
    success, k3, node2 = repeat_expr(k2)
    if not success:
        return True, k1, node1 + [3]  # {'session': node1 + [3]}
    return True, k3, node1 + [node2]  # {'session': node1 + [node2]}


@memoize
def session_expr(k):
    """session_expr      <- day LINK2 slot_expr"""
    success, k1, node1 = day(k)
    if not success:
        return False, k, None
    success, k2, _ = link2(k1)
    success, k3, node2 = slot_expr(k2)
    if not success:
        return False, k, None
    return True, k3, [node1] + node2


@memoize
def repeat_expr(k):
    """repeat_expr       <- WEEKLY / FORTNIGHT OPTSPC parity"""
    success, k1, weekly = token('WEEKLY', k)
    if success:
        return True, k1, 3
    success, k1, fortnight = token('FORTNIGHT', k)
    if not success:
        return False, k, None
    success, k2, _ = optspc(k1)
    success, k3, p = parity(k2)
    if not success:
        return False, k, None
    return True, k3, p


@memoize
def parity(k):
    """parity            <- II / I / num"""
    success, k1, _ = token('PARITY_II', k)
    if success:
        return True, k1, 2
    success, k1, _ = token('PARITY_I', k)
    if success:
        return True, k1, 1
    success, k1, n = num(k)
    p = n.value() if success else 0
    if p == 1 or p == 2:
        return True, k1, p
    return False, k, None


@memoize
def day(k):
    """day               <- MON / TUE / WED / THU / FRI / SAT"""
    for d in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']:
        success, k1, node = token(d, k)
        if success:
            return True, k1, node.type
    return False, k, None


@memoize
def slot_expr(k):
    """slot_expr         <- time_expr LINK3 time_expr"""
    success, k1, node1 = time_expr(k)
    if not success:
        return False, k, None
    success, k2, _ = link3(k1)
    if not success:
        return False, k, None
    success, k3, node2 = time_expr(k2)
    if not success:
        return False, k, None
    return True, k3,  [node1, node2]


@memoize
def time_expr(k):
    """time_expr         <- digital_time_expr / written_time_expr"""
    success, k1, node1 = digital_time_expr(k)
    if success:
        return True, k1, node1
    return written_time_expr(k)


@memoize
def digital_time_expr(k):
    """digital_time_expr <- num_hour COLON NUM2"""
    success, k1, h = num_hour(k)
    if not success:
        return False, k, None
    success, k2, _ = token('COLON', k1)
    if not success:
        return False, k, None
    success, k3, n = token('NUM2', k2)
    m = n.value() if success else -1
    if 0 <= m <= 59:
        return True, k3, {'h': h, 'm': m}
    return False, k, None


@memoize
def written_time_expr(k):
    """written_time_expr <- hour_expr OPTSPC minute_expr / hour_expr / num_hour"""
    success, k1, h = hour_expr(k)
    if success:
        success, k2, _ = optspc(k1)
        success, k3, m = minute_expr(k2)
        if success:
            return True, k3, {'h': h, 'm': m}
        return True, k1, {'h': h, 'm': 0}

    success, k1, h = num_hour(k)
    if success:
        return True, k1, {'h': h, 'm': 0}
    return False, k, None


@memoize
def hour_expr(k):
    """hour_expr         <- num_hour OPTSPC HOUR"""
    success, k1, h = num_hour(k)
    if not success:
        return False, k, None
    success, k2, _ = optspc(k1)
    success, k3, t = token('HOUR', k2)
    if not success:
        return False, k, None
    return True, k3, h


@memoize
def num_hour(k):
    """num_hour          <- NUM2 / NUM1"""
    success, k1, t = token('NUM2', k)
    h = t.value() if success else -1
    if success and 0 <= h <= 23:
        return True, k1, h
    success, k1, t = token('NUM1', k)
    h = t.value() if success else -1
    if success and 0 <= h <= 23:
        return True, k1, h
    return False, k, None


@memoize
def minute_expr(k):
    """minute_expr       <- num_minute OPTSPC MINUTE / num_minute"""
    success, k1, m = num_minute(k)
    if not success:
        return False, k, None
    success, k2, _ = optspc(k1)
    success, k3, _ = token('MINUTE', k2)
    if success:
        return True, k3, m
    return True, k1, m


@memoize
def num_minute(k):
    """num_minute        <- NUM2 / NUM1"""
    success, k1, t = token('NUM2', k)
    m = t.value() if success else -1
    if success and 0 <= m <= 59:
        return True, k1, m
    success, k1, t = token('NUM1', k)
    m = t.value() if success else -1
    if success and 0 <= m <= 59:
        return True, k1, m
    return False, k, None


def num(k):
    """num       <- NUM2 / NUM1"""
    success, k1, n = token('NUM2', k)
    if success:
        return True, k1, n
    success, k1, n = token('NUM1', k)
    if success:
        return True, k1, n
    return False, k, None


@memoize
def optspc(k):
    success, k1, s = token('SPC', k)
    if not success:
        return True, k, None
    return True, k1, s


@memoize
def link1(k):
    """link1     <- optspc COMMA optspc / optspc"""
    success, k1, _ = optspc(k)
    success, k2, _ = token('COMMA', k1)
    if not success:
        return True, k1, None
    success, k3, s = optspc(k2)
    return True, k3, None


@memoize
def link2(k):
    """link2     <- OPTSPC DAS OPTSPC / OPTSPC"""
    success, k1, _ = optspc(k)
    success, k2, _ = token('DAS', k1)
    if not success:
        return True, k1, None
    success, k3, s = optspc(k2)
    return True, k3, None


@memoize
def link3(k):
    """link3     <- OPTSPC SEP OPTSPC / SPC"""
    success, k1, _ = optspc(k)
    success, k2, _ = token('SEP', k1)
    if not success:
        return token('SPC', k)
    success, k3, _ = optspc(k2)
    return True, k3, None


def parse(text):
    global buffer

    buffer = ud.unidecode(text.lower())
    return schedule_expr(0)


table = []


def fill_table():
    global table

    def counter():
        counter.tick += 1
        return counter.tick

    table = []
    counter.tick = -1
    table.append({i: [counter() for _ in range(6)] for i in range(8, 23)})
    counter.tick = 95
    table.append({i: [counter() for _ in range(6)] for i in range(8, 23)})


def text2schedule(text):
    fill_table()
    success, end, sessions = parse(text)
    if not success:
        return

    s = []
    for session in sessions:
        d = session[0]
        h1 = session[1]['h']
        # m1 = session[1]['m']
        h2 = session[2]['h']
        m2 = session[2]['m']
        h2 = h2 if not m2 else h2 + 1
        r = session[3]
        if r & 1:
            for h in range(h1, h2):
                s.append(table[0][h][d])
        if r & 2:
            for h in range(h1, h2):
                s.append(table[1][h][d])

    return s
