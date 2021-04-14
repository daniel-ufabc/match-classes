import config
from models import CourseApplication, ClassApplication, mapping
from utils import sheets
from utils.sheets import xlsx2csvs, check_xlsx, check_csv


def import_data(domain, filename, update=False):
    feedback = check_xlsx(filename) if domain == 'preferences' else check_csv(filename)
    if feedback is not None:
        return {'error': 'Formato de arquivo incorreto. ' + feedback}
    if domain == 'preferences':
        filenames = xlsx2csvs(filename)
        print(f'config.ABSOLUTE_DATA_SUBDIR = {config.ABSOLUTE_DATA_SUBDIR}')
        print(filenames)
        return {
            'courses': CourseApplication.import_csv(filenames['Disciplinas'], clear_table=True),
            'classes': ClassApplication.import_csv(filenames['Turmas'], clear_table=True)
        }

    return mapping[domain].import_csv(filename, ignore=not update, on_duplicate_key_update=update)


def export_data(domain):
    if domain == 'preferences':
        return {'basename': sheets.csvs2xlsx(**{
            'Disciplinas': CourseApplication.export_csv(),
            'Turmas': ClassApplication.export_csv()
        })}
    return {'basename': mapping[domain].export_csv()}
