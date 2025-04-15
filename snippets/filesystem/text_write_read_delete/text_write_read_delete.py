import os

# Open a new file for writing
#   NOTE: This will create a new file if it doesn't exist,
#   or overwrite the existing file.
write_file = open('new_file.txt','w')
# Write a string to the file
write_file.write('Hello, World!')
# Always close the file when finished writing
write_file.close()

# Print the contents of the current directory, to see the new file
print(os.listdir())

# Open the file for reading
read_file = open('new_file.txt','r')
# Read the contents of the file into a string
file_contents = read_file.read()
# Print the contents of the file
print(file_contents)
# Close the file when finished reading
read_file.close()

# Delete the file
os.remove('new_file.txt')
# Print the contents of the current directory, to see the file has been deleted
print(os.listdir())

