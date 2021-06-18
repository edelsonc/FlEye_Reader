# Camera Video Reader
Python commandline script to 


# Installing & Usage

## Requirements
Running this programs requires `python3.8` or newer and `pipenv`. If you don't have these installed a guide for their installation can be found [here](https://www.python.org/downloads/) and [here](https://docs.python-guide.org/dev/virtualenvs/#:~:text=Pipenv%20%26%20Virtual%20Environments%20%C2%B6%201%20Make%20sure,installed%20packages%20%C2%B6.%20...%205%20Next%20steps%20%C2%B6).

## Installing
Installing `FlEye Reader` is as simple as clone this repository setting up a new `pipenv` environment. This can be done with the following code snippet

```
$ git clone https://github.com/edelsonc/FlEye_Reader
$ cd FlEye_Reader
$ pipenv install
```
Now you can enter your new virtual environment by calling `pipenv shell`.

## Usage
`FlEye Reader` uses the `Click` module to create a simple commandline interface. The script expects two arguments, `READ_FILE` and `WRITE_FILE`. These are the raw binary video from the fly camera and the location of the new reformatted video, respectively. To run the script execute the following code in your `pipenv` shell

```
$ python FlEye_Reader my_data_file.bin my_write_file.bin
```
Finally, you can always call help for a quick description of the script
```
$ python FlEye_Reader --help
Usage: FlEye_Reader.py [OPTIONS] READ_FILE WRITE_FILE

  Commandline program to validate and reformat data from the fly vision
  camera.

Options:
  --help  Show this message and exit.
```

# Reformatted Data
The main function of this script is to validate and reformatted the data from the fly camera in a way that's simpler to use with `MATLAB` or other data analysis language. An example of working with this new format is given in `example_read_from_res.m`. It's content is also shown below

```
% simple example script of how to read reformatted data into matlab
data_file = fopen("Data\reformatted_data.bin");
datau32 = fread(data_file, '*uint32', 'b');
data_matrix = reshape(datau32, 256, []);
imu = data_matrix(195:end,:);
imu = imu(1:20,:);  % removes the spacers added to pad the frame to 1024 bytes

% convert the u32 into it's correct format of i16
imui16 = typecast(uint16(imu(:)), 'int16');
imui16 = reshape(imui16, 20, []);


fclose(data_file);
```
