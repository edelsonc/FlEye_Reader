% simple example script of how to read reformatted data into matlab
file_name = fullfile("C:", "path", "to", "my", "data.bin");
data_file = fopen(file_name);
datau32 = fread(data_file, '*uint32', 'b');
data_matrix = reshape(datau32, 256, []);
imu = data_matrix(197:217,:);
imu = imu(1:20,:);

% convert the u32 into it's correct format of i16
imui16 = typecast(uint16(imu(:)), 'int16');
imui16 = reshape(imui16, 20, []);

fclose(data_file);
