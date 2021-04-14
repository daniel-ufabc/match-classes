#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import os
import sys
import subprocess

import config
from utils.files import data_filename as fn
from utils.misc import log
from schedule.parser import text2schedule as parse_schedule
from driver.extract import get_courses_and_classes_data, \
    get_students, get_applications, get_parameters
from driver.index import create_classes_and_courses_indexes, \
    save_classes_and_courses, save_criteria, \
    create_criteria_indexes, create_parameters_index, \
    save_parameters, create_students_index, save_students


assert len(sys.argv) == 3, 'execute.py  <max_search>  <default_parameter>'
max_search = int(sys.argv[1])
default_parameter = int(sys.argv[2])

# DISCIPLINAS E TURMAS
log('processando disciplinas e turmas...')
classes_of_course, classes, criteria_list = get_courses_and_classes_data()
course_codes_list = list(classes_of_course.keys())
save_classes_and_courses(course_codes_list, classes_of_course)
save_criteria(criteria_list)
criteria_expr2index, index2criteria_expr = create_criteria_indexes(criteria_list)

with open(fn('disciplinas'), 'w') as f:
    for i, code in enumerate(course_codes_list):
        n = len(classes_of_course[code])
        f.write(f'{i}:{n}\n')

with open(fn('turmas'), 'w') as f:
    for i, code in enumerate(course_codes_list):
        for j, class_code in enumerate(classes_of_course[code]):
            k = criteria_expr2index[classes[class_code]['criteria']]
            carga = classes[class_code]['load']
            vagas = classes[class_code]['vacancies']
            encontros = parse_schedule(classes[class_code]['schedule'])
            ne = len(encontros)
            encontros_str = ','.join([str(encontro) for encontro in encontros])
            f.write(f'{i}:{j}:{k},0;{carga};{vagas};{ne},{encontros_str}\n')

del classes
del criteria_expr2index

# Extrai dados dos alunos
log('processando alunos...')
students, carga = get_students()
students_list = list(students.keys())

student2index, index2student = create_students_index(students_list)
save_students(students_list)


# TOTAIS
log('calculando totais...')
na = len(students_list)
nd = len(course_codes_list)
nc = len(criteria_list)
bm = max_search

with open(fn('totais'), 'w') as f:
    f.write(f'{nd};{na};{nc},{default_parameter};{bm}\n')


# Analisa critérios
log('analisando critérios...')
param_list = get_parameters(criteria_list)
del criteria_list
param2index, index2param = create_parameters_index(param_list)
save_parameters(param_list)

# Prepara arquivo com os parâmetros de cada aluno
log('preparando arquivo com os parâmetros de cada aluno...')
np = len(param_list)
INT_MIN = -2147483648
with open(fn('students_params.txt'), 'w') as f:
    f.write(f'{na} {np}\n')
    for code, props in students.items():
        f.write(str(student2index[code]))
        for i in range(np):
            value = int(float(props.get(index2param[i], INT_MIN / 1000)) * 1000)
            f.write(f' {value}')
        f.write('\n')

del students
del param_list
del index2param
del student2index

# Prepara arquivo com os critérios de cada ordenação
log('preparando arquivo com os critérios de cada ordenação...')
with open(fn('criteria.txt'), 'w') as f:
    f.write(f'{nc}\n')
    for i in range(nc):
        expr = index2criteria_expr[i]
        params = expr.split('>')
        nps = len(params)
        f.write(f'{nps}')
        for param in expr.split('>'):
            j = param2index[param]
            f.write(f' {j}')
        f.write('\n')

del index2criteria_expr
del param2index

# Ordena os alunos (via sort_students.c)
log('chamando sort_students...')
with open('/tmp/debug_sort', 'w') as f:
    return_code = subprocess.run([config.SORT_STUDENTS_BINARY_FILENAME, fn('students_params.txt'),
                                  fn('criteria.txt'), fn('output.txt')], stderr=f).returncode
if return_code:
    with open(fn('output'), 'w') as f:
        f.write(f'Processo de ordenação dos alunos retornou com erro {return_code}.')
    sys.exit(1)


# ALUNOS
log('gravando arquivo de alunos...')
with open(fn('alunos'), 'w') as g:
    with open(fn('output.txt')) as f:
        for j, line in enumerate(f):
            c = carga[index2student[j]]
            g.write(f'{j}:{c};{line.strip()};0\n')

del carga


# PEDIDOS
log('pedidos...')
course_apps, class_apps = get_applications()
course2index, index2course, class2index, index2class = \
    create_classes_and_courses_indexes(course_codes_list, classes_of_course)

with open(fn('pedidos'), 'w') as f:
    for i in range(na):
        student = index2student[i]
        if student in course_apps:
            ndp = len(course_apps[student])
            f.write(f'{i}:{ndp}')
            for course, classes in class_apps[student].items():
                if course in course_apps[student]:
                    cd = course2index[course]
                    ntp = len(classes)
                    if ntp:
                        cls = ','.join([str(class2index[class_code]) for class_code in classes])
                        f.write(f';{cd}:{ntp},{cls}')
                    else:
                        # This should never happen
                        f.write(f';{cd}:0')
            f.write('\n')


# Executa o programa do Vinícius
log('executando o programa "match" para fazer o escalonamento...')
input_files = ['totais', 'disciplinas', 'turmas', 'alunos', 'pedidos']
output_files = ['listas', 'info_disciplinas', 'info_turmas', 'resolvidos', 'indeferidos', 'turmas2', 'alunos2']
files = input_files + output_files

with open(fn(config.SCHEDULER_OUTPUT_FILE), 'w') as f:
    args = [config.SCHEDULER_BINARY_FILENAME] + [fn(file) for file in files]
    return_code = subprocess.call(args, stdout=f)

if return_code:
    percent = 0
    last_line = ''

    def read_feedback(enc='utf-8'):
        global percent, last_line, line
        with open(fn(config.SCHEDULER_OUTPUT_FILE), encoding=enc) as h:
            for line in h:
                last_line = line
                if '+' in line:
                    # Vinícius imprime um char para cada 2% de progresso
                    percent = 2 * len(line.strip())

    try:
        read_feedback()
    except UnicodeDecodeError:
        read_feedback('latin1')

    if '+' in last_line:
        with open(fn(config.SCHEDULER_OUTPUT_FILE), 'w') as f:
            f.write(f'"match" retornou código de erro {return_code} após {percent}% de progresso.')
    sys.exit(1)

# Recupera tabelas
log('recuperando tabelas a partir dos dados de saída de "match"...')
with open(fn('listas')) as f, open(fn('listas.csv'), 'w') as g:
    for line in f:
        cd, ct, ca = line.split(',')
        course_code = index2course[int(cd)]
        class_code = index2class[course_code][int(ct)]
        student_code = index2student[int(ca)]
        g.write(f'{course_code},{class_code},{student_code}\n')

with open(fn('info_disciplinas')) as f, open(fn('info_disciplinas.csv'), 'w') as g:
    writer = csv.writer(g, delimiter=config.CSV_DELIMITER, quotechar=config.CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
    header = ['CÓDIGO DA DISCIPLINA', 'DEMANDA TOTAL', 'DEMANDA REPRIMIDA', 'TOTAIS DE MATRÍCULA',
              'TOTAIS DE VAGAS DISPONÍVEIS', 'TOTAIS DE VAGAS OCIOSAS']
    writer.writerow(header)
    for line in f:
        cd, *rest = line.strip().split(',')
        course_code = index2course[int(cd)]
        writer.writerow([course_code] + rest)

with open(fn('info_turmas')) as f, open(fn('info_turmas.csv'), 'w') as g:
    writer = csv.writer(g, delimiter=config.CSV_DELIMITER, quotechar=config.CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
    header = ['CÓDIGO DA DISCIPLINA', 'CÓDIGO DA TURMA', 'DEMANDA PELA TURMA', 'DEMANDA REPRIMIDA',
              'NÚMERO DE MATRICULADOS', 'VAGAS DISPONÍVEIS', 'VAGAS OCIOSAS']
    writer.writerow(header)
    for line in f:
        cd, ct, *rest = line.strip().split(',')
        course_code = index2course[int(cd)]
        class_code = index2class[course_code][int(ct)]
        writer.writerow([course_code, class_code] + rest)

for filename in ['resolvidos', 'indeferidos']:
    with open(fn(filename)) as f, open(fn(filename + '.csv'), 'w') as g:
        for line in f:
            ca, cd, i = line.split(',')
            course_code = index2course[int(cd)]
            student_code = index2student[int(ca)]
            i = i.strip()
            g.write(f'{course_code},{student_code},{i}\n')

log('gerando arquivo .zip...')
os.chdir(fn(''))
# The following line contains a hack to deal with turmas2 and alunos2.
return_code = subprocess.call(['zip', '-r', 'tabelas.zip'] +
                              [filename + ('.csv' if '2' not in filename else '') for filename in output_files])

with open(fn(config.SCHEDULER_OUTPUT_FILE), 'a') as f:
    if return_code:
        f.write('(driver) Não foi possível gerar arquivo .zip com os dados gerados.')
        sys.exit(1)
    f.write('(driver) Escalonamento concluído com sucesso.')
log('terminado.')
