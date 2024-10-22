
def binary_to_text(binary_data):
 text = "
  for i in range(0, len(binary_data), 8):
    byte = binary_data[i:i+8]
    text += chr(int(byte, 2))
  return text
def calculate_redundant_bits(m):
  for i in range(m):
   if (2**i >= m + i + 1):
     return i
def receiver():
 hamming_data = read_channel()
 nr = calculate_redundant_bits(len(
hamming_data))
 error_pos = detect_error(hamming_data, nr)
 if error_pos == 0:
  print("No error detected.")
  correct_data = hamming_data
 else:
  print(f"Error detected at position: {error_pos}")
  correct_data = correct_error(hamming_data,
  error_pos)
data_without_redundant_bits=remove_redundant_bits(correct_data, nr)
ascii_text = binary_to_text(data_without_redundant_bits)
print(f"Received text: {ascii_text}")
