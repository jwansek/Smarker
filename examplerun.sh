zip -r 100301654.zip ./ExampleSubmission/
python ./mark.py -s 100301654.zip -a ./ExampleAssessments/example.yml -f tex -o auto
rm 100301654.zip
pdflatex 100301654_report.tex
rm -v *.log
rm -v *.aux
rm -v *.tex
rm -v *_test_report.pdf