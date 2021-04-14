import json
from utils.files import data_filename as fn


def create_classes_and_courses_indexes(course_codes_list: list, classes_of_course: dict):
    course2index = dict()
    index2course = dict()
    for i, course in enumerate(course_codes_list):
        course2index[course] = i
        index2course[i] = course

    class2index = dict()
    index2class = dict()
    for course_code in course_codes_list:
        index2class[course_code] = dict()
        for j, class_code in enumerate(classes_of_course[course_code]):
            class2index[class_code] = j
            index2class[course_code][j] = class_code

    return course2index, index2course, class2index, index2class


def load_classes_and_courses():
    with open(fn('course_codes_list.json')) as f:
        course_codes_list = json.load(f)

    with open(fn('classes_of_course.json')) as f:
        classes_of_course = json.load(f)

    return course_codes_list, classes_of_course


def save_classes_and_courses(course_codes_list: list, classes_of_course: dict):
    with open(fn('course_codes_list.json'), 'w') as f:
        json.dump(course_codes_list, f)

    with open(fn('classes_of_course.json'), 'w') as f:
        json.dump(classes_of_course, f)


def save_criteria(criteria_list: list):
    with open(fn('criteria_list.json'), 'w') as f:
        json.dump(criteria_list, f)


def load_criteria():
    with open(fn('criteria_list.json')) as f:
        criteria_list = json.load(f)

    return criteria_list


def create_criteria_indexes(criteria_list):
    criteria_expr2index = dict()
    index2criteria_expr = dict()
    for i, expr in enumerate(criteria_list):
        criteria_expr2index[expr] = i
        index2criteria_expr[i] = expr

    return criteria_expr2index, index2criteria_expr


def create_parameters_index(param_list):
    param2index = dict()
    index2param = dict()
    for i, param in enumerate(param_list):
        param2index[param] = i
        index2param[i] = param

    return param2index, index2param


def save_parameters(param_list):
    with open(fn('param_list.json'), 'w') as f:
        json.dump(param_list, f)


def load_parameters():
    with open(fn('param_list.json')) as f:
        param_list = json.load(f)

    return param_list


def create_students_index(students_list):
    student2index = dict()
    index2student = dict()
    for i, code in enumerate(students_list):
        student2index[code] = i
        index2student[i] = code

    return student2index, index2student


def save_students(students_list):
    with open(fn('students_list.json'), 'w') as f:
        json.dump(students_list, f)


def load_students():
    with open(fn('students_list.json')) as f:
        students_list = json.load(f)

    return students_list
