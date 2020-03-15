## <div align="left"> Spelling-Error-Corrector </div>

An isolated word spelling error corrector based on the noisy channel model

### <div align="left"> Requirements </div>
```
1. Python
2. Regex
3. Argument Parser
```

### <div align="left"> How to Run? </div>

In order to run Spelling-Error-Corrector, execute the following from the command line under **Code Files/**:

```
> python3 corrector.py --corpus [CORPUS_FILE] --spell_errors [SPELL_ERRORS_FILE] --misspelled [MISSPELLED_FILE]
--correct [CORRECT_FILE] --smooth --print_confusions
```

```
where [CORPUS_FILE] -> path of corpus.txt (required),
      [SPELL_ERRORS_FILE] -> path of spell_errors.txt(required),
      [MISSPELLED_FILE] -> path of misspelled words file(required),
      [CORRECT_FILE] -> path of correct words file(not required),
      smooth -> whether use alpha smoothing or not(not required),
      print_confusions -> whether print confusion matrices or not(not required)
```


### <div align="left"> Notes </div>
```
1. Algorithm prints corrected versions of misspelled words in a file named output.txt.
2. output.txt is located in the same directory with the execution.
3. [CORRECT_FILE] is not required while execution.
4. It is required when calculating accuracy is needed.
5. smooth is not required.
6. If you execute algorithm with smooth, it implements alpha smoothing.
Otherwise, it does not implement smoothing.
7. If you execute algorithm with print_confusions, it prints confusion matrices by
creating new text files. Otherwise, it does not print.
```
