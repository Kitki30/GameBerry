# Kitki30 Gameberry Download List File

## What is download list
Download list is used in Gameberry installer,
it tells the installer what files to download,
what folders to create and many more!
Please read this guide if you want to contribute or make custom Gameberry version!

## Basic elements of Download List

### Info elements
Info elements tell the installer if file is a list and version of the list!
They need to be included or the list will not be recognized as a list,
and installer will abort its work!

Kitki30-Gameberry-Download-List-File - Needs to be included (Line 1)
version 1.0 - Version of Download List - Needs to be included (Line 2)

Begining of the list will look like this
```
Kitki30-Gameberry-Download-List-File
version 1.0
```

### START
START command needs to be included after info elements of download list
Your download list should look like this:
```
Kitki30-Gameberry-Download-List-File
version 1.0
START
```

## Commands
Commands are included after START of the Download List,
they tell installer what to do!

Example:
```
Kitki30-Gameberry-Download-List-File
version 1.0
START
(you add commands here)
```

### download
Makes get request to URL and saves content to specified file!

Elements of download command
First line of download: download
Second line of download: file path to were to save the file
Third line of download: URL to content that you want to download
> [!NOTE]
> File path should not be starting with / installer automaticly adds it at begining of the path!
> [!NOTE]
> Link to files from github should be link to raw file or the installer will download the code of github page!

Example:
```
download
file.py
https://www.kitki30.tk/file.py
```

### folder
Makes folder on devices flash memory

Elements of folder command:
First line: folder
Second line: folder name
> [!NOTE]
> Folder path should not be starting with / installer automaticly adds it at begining of the path!

Example:
```
folder
my_folder
```

### message
Prints message with print() command
Message is also logged in log

Elements of message command:
First line: message
Second line: your message

Example:
```
message
Hello
```

User using installer will see your message!

### log-message
Same as message command but shows it only in log!

Elements of log-message command:
First line: log-message
Second line: message you want to show in log

Example:
```
log-message
Hello
```

Message will be written to log

### comment
Comments in list
Ignored by installer

Comments can only be one line

Example:
```
comment
Hello
```

### wait
Wait some time before reading other lines of the list
Uses time.sleep() for waiting

Elements of wait command:
First line: wait
Second line: time you want to wait

Example:
```
wait
0.5
```

### write
Writes something to file!

Elements of write command:
First line: write
Second line: file name
Third line: content
> [!NOTE]
> File path should not be starting with / installer automaticly adds it at begining of the path!
> [!NOTE]
> Content needs to fit in one line or installer will show unknown command errors!
> [!NOTE]
> This command will overwrite the file you are writing to, to append content to file use write-append command

Example:
```
write
file.py
# Content
```

### write-append
Appends / writes something to file!

Elements of write-append command:
First line: write-append
Second line: file name
Third line: content
> [!NOTE]
> File path should not be starting with / installer automaticly adds it at begining of the path!
> [!NOTE]
> Content needs to fit in one line or installer will show unknown command errors!

Example:
```
write
file.py
# Content
```

### Variables
Comming soon...

## Ending Download List
Simply add END at end of the list
This will tell the installer to stop reading the download list!

Example:
```
Kitki30-Gameberry-Download-List-File
version 1.0
START
comment
Example command
END
```

You cannot add any commands after that!