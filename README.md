Code hỗ trợ tạo dữ liệu cho bài toán text detection và key infomation extraction từ file odt.

Các bước sinh dữ liệu:
- Tạo file .odt (có thể dùng libre office): phần text dạng \$(key1), \$(key2),... có thể bị thay thế
- Tạo thông tin thay thế: key_dict gồm key_name:{replace_key:[key1, key2, ...], label:[...]}
- Cài đặt file config yml
- Chạy file odt_to_kie.py hoặc odt_to_labelme.py

Dữ liệu sinh:
- Text detection: gồm image và json file được load bởi tool Labelme
- Key infomation extraction: json file load bởi tool https://github.com/ndgnuh/relation-tagger