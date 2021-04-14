#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <time.h>

#define EMPTY INT_MIN

int **_A;         // "alunos" with scrambled rows (see description of "alunos" below)
int _nps;         // número de parâmetros no critério atual (see next line)
int *_cri;        // critério atual (vetor de parâmetros)
int **_scratch;   // extra space for merge_sort (to sort **_A)

void merge(int p, int q, int r) {
    int i = p, k = p, j = q;

    while (i < q && j < r) {
        int less = 1;

        // Compares **_A[i] with **_A[j]
        for (int l = 0; l < _nps; l ++) {
            int param = _cri[l];
            if (_A[i][param] < _A[j][param])
                break;
            if (_A[i][param] > _A[j][param]) {
                less = 0;
                break;
            }
        }

        _scratch[k ++] = less ? _A[i ++] : _A[j ++];
    }

    while (i < q)
        _scratch[k ++] = _A[i ++];

    while (j < r)
        _scratch[k ++] = _A[j ++];

    for (k = p; k < r; k ++)
        _A[k] = _scratch[k];
}

// Sort the elements of array **_A according to criterion _cri
void merge_sort(int p, int r) {
    fprintf(stderr, "p = %d, r = %d\n", p, r);
    if (r < p + 2)
        return;

    int q = (p + r) / 2;
    merge_sort(p, q);
    merge_sort(q, r);
    merge(p, q, r);
}

void error(char *msg) {
    if (msg != NULL)
        fprintf(stderr, "%s\n", msg);
    else {
        fprintf(stderr, "use as follows:\n\n\t sort_students  students_params_filename  ");
        fprintf(stderr, "criteria_filename  output_filename\n\n");
    }
    exit(1);
}

int main(int ac, char **av) {
    if (ac != 4)
        error(NULL);

    fprintf(stderr, "opening input files\n");
    FILE *st = fopen(av[1], "r");
    FILE *cr = fopen(av[2], "r");

    if (st == NULL || cr == NULL)
        error(NULL);

    int na;   // número de alunos
    int np;   // número de parâmetros
    int nc;   // número de critérios

    if (fscanf(st, "%d %d", &na, &np) != 2)
        error("Verificar arquivo com os parâmetros dos alunos!\n");
    if (fscanf(cr, "%d", &nc) != 1)
        error("Verificar arquivo de critérios!\n");

    // Matriz nc x np
    // 1 critério por linha
    // 1 parâmetro por coluna
    // uma linha pode ser mais curta que as outras se o critério envolver menos parâmetros
    // parâmetros mais à esquerda têm mais prioridade
    int **criterio = (int **) malloc(nc * sizeof(int *));
    int *n_params = (int *) malloc(nc * sizeof(int));

    if (criterio == NULL || n_params == NULL)
        error("Could not allocate memory (criterio, n_params).\n");

    fprintf(stderr, "reading criteria\n");
    for (int i = 0; i < nc; i ++) {
        criterio[i] = (int *) malloc(np * sizeof(int));
        if (criterio[i] == NULL)
            error("Could not allocate memory.\n");
        int nps;

        // lê o número de parâmetros dos quais depende o i-ésimo critério
        if (fscanf(cr, "%d", &nps) != 1)
            error("Verificar arquivo de critérios!\n");
        if (nps > np) {
            fprintf(stderr, "Erro: mais de %d parâmetros no %d-ésimo critério.\n", np, i + 1);
            error("Verificar arquivo de critérios!\n");
        }

        // lê parâmetros que definem o i-ésimo critério:
        n_params[i] = nps;
        int j;
        for (j = 0; j < nps && fscanf(cr, "%d", criterio[i] + j) == 1; j ++);
        if (j < nps) {
            fprintf(stderr, "Fim prematuro do critério %d.\n", i + 1);
            error("Verificar arquivo de critérios!\n");
        }
    }

    fclose(cr);

    // Matriz aluno tem dimensões na x (np + 1)
    // aluno[j][np] tem o código do aluno j (não necessariamente é j)
    // aluno[j][0..(np-1)] tem os parâmetros daquele aluno
    // ordens[0], ordens[1], etc são as ordenações pelos varios critérios
    int **aluno = (int **) malloc(na * sizeof(int *));
    if (aluno == NULL)
        error("Could not allocate memory (aluno).\n");

    for (int j = 0; j < na; j ++) {
        aluno[j] = (int *) malloc((np + 1)* sizeof(int));
        if (aluno[j] == NULL)
            error("Could not allocate memory (row of aluno).\n");
    }

    int ***ordens = (int ***) malloc(nc * sizeof(int **));
    if (ordens == NULL)
        error("Could not allocate memory (ordens).\n");
    _scratch = (int **) malloc(na * sizeof(int *));
    if (_scratch == NULL)
        error("Could not allocate memory (_scratch).\n");

    ordens[0] = aluno;

    srand(time(NULL));

    fprintf(stderr, "randomizing students before sorting\n");
    for (int i = 0; i < nc; i ++) {
        if (i > 0) {
            ordens[i] = (int **) malloc(na * sizeof(int *));
            if (ordens[i] == NULL)
                error("Could not allocate memory (row of ordens).\n");
            for (int j = 0; j < na; j ++)
                ordens[i][j] = aluno[j];
        }

        // Randomize before sorting (Vini's request).
        for (int j = na - 1; j > 0; j --) {
            int k = rand() % (j + 1);
            int *tmp = ordens[i][j];
            ordens[i][j] = ordens[i][k];
            ordens[i][k] = tmp;
        }
    }

    fprintf(stderr, "reading students' params\n");
    for (int j = 0; j < na; j ++) {
        // lê código do aluno:
        if (fscanf(st, "%d", aluno[j] + np) != 1) {
            fprintf(stderr, "Erro: não foi possível ler o %d-ésimo aluno do arquivo.\n", j + 1);
            error("Verificar arquivo de alunos.\n");
        }

        // lê parâmetros do aluno:
        for (int k = 0; k < np; k ++) {
            if (fscanf(st, "%d", aluno[j] + k) != 1) {
                fprintf(stderr, "Erro: aluno %d, no %d-ésimo parâmetro.\n", aluno[j][np], k + 1);
                error("Verificar arquivo de alunos.\n");
            }
        }
    }

    // Students file no longer needed.
    fclose(st);

    // Sort students according to each criterion.
    fprintf(stderr, "sorting students according to each criterion\n");
    for (int i = 0; i < nc; i ++) {
        _nps = n_params[i];
        _cri = criterio[i];
        _A = ordens[i];
        merge_sort(0, na);
    }

    // Free some memory
    fprintf(stderr, "freeing n_params, _scratch, criterio\n");
    free(n_params);
    free(_scratch);
    for (int i = 0; i < nc; i ++)
        free(criterio[i]);
    free(criterio);

    // Space to store the final "grades" of all the students.
    int **final = (int **) malloc(na * sizeof(int *));
    if (final == NULL)
        error("Could not allocate memory (final).\n");

    for (int j = 0; j < na; j ++) {
        final[j] = (int *) malloc(nc * sizeof(int));
        if (final == NULL)
            error("Could not allocate memory (row of final).\n");
    }

    // Inefficient: essentially matrix transpose.
    // Many page faults... so sad...
    fprintf(stderr, "computing grades\n");
    for (int i = 0; i < nc; i ++)
        for (int j = 0; j < na; j ++)
            final[ordens[i][j][np]][i] = j;

    // Free some more memory
    for (int j = 0; j < na; j ++)
        free(aluno[j]);
    for (int i = 0; i < nc; i ++)
        free(ordens[i]);
    free(ordens);

    // Generate output.
    fprintf(stderr, "generating output\n");
    FILE *out = fopen(av[3], "w");
    for (int j = 0; j < na; j ++) {
        fprintf(out, "%d", final[j][0]);
        for (int i = 1; i < nc; i ++)
            fprintf(out, ",%d", final[j][i]);
        fprintf(out, "\n");
    }
    fclose(out);

    for (int j = 0; j < na; j ++)
        free(final[j]);
    free(final);

    return 0;
}