The code supports generating data for the text detection problem and key information extraction from the odt file.

Process: Load odt &rarr; Replace key &rarr; Save as pdf &rarr; Load pdf &rarr; Read texts and bounding boxes &rarr; save as Text Detection or KIE

Steps to generate data:

- Create an .odt file (can use libre office): the text is in the form of \$(key1), \$(key2),... can be replaced
- Generate replacement information: key_dict includes key_name:{replace_key:[key1, key2, ...], label:[...]}
- Setting the config file yml
- Run the file odt_to_kie.py or odt_to_labelme.py

Birth data:
- Text detection: includes image and json file loaded by Labelme tool
- Key information extraction: json file loaded by tool https://github.com/ndgnuh/relation-tagger
