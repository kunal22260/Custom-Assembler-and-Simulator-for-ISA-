import sys
class Memory:
    def __init__(self):
        self.data = [0] * 128
    
    def fetchData(self, address):
        return self.data[address]
    
    def storeData(self, address, value):
        self.data[address] = value
    
    def dump(self):
        for data in self.data:

            sys.stdout.write(format(data, '016b') + '\n')
class RegisterFile:
    def __init__(self):
        self.registers = [0] * 7
        self.flags = 0

    def getValue(self, register):
        if register == 'FLAGS':
            return self.flags
        else:
            register_num = int(register) - 1
            return self.registers[register_num]

    def setValue(self, register, value):
        if register == 'FLAGS':
            self.flags = value
        else:
            register_num = int(register) - 1
            self.registers[register_num] = value

    def dump(self):
        register_values = ' '.join(format(reg, '016b') for reg in self.registers)
        flags_value = format(self.flags, '016b')
        sys.stdout.write(f"{register_values} {flags_value}\n")

class ExecutionEngine:
    @staticmethod
    def execute(instruction, rf, pc):
        opcode = (instruction >> 11) & 0b11111

        if opcode == 0b00000:  # Addition - Type A
            dest_register = (instruction >> 8) & 0b111
            src_register1 = (instruction >> 5) & 0b111
            src_register2 = instruction & 0b111
            result = rf.getValue(src_register1) + rf.getValue(src_register2)
            rf.setValue(dest_register, result)
            if result > 255:
                rf.setValue(dest_register, 0)
                rf.setValue('FLAGS', 1)

        elif opcode == 0b00001:  # Subtraction - Type A
            dest_register = (instruction >> 8) & 0b111
            src_register1 = (instruction >> 5) & 0b111
            src_register2 = instruction & 0b111
            if rf.getValue(src_register2) > rf.getValue(src_register1):
                rf.setValue(dest_register, 0)
                rf.setValue('FLAGS', 1)
            else:
                result = rf.getValue(src_register1) - rf.getValue(src_register2)
                rf.setValue(dest_register, result)

        elif opcode == 0b00010:  # Move Immediate - Type B
            dest_register = (instruction >> 8) & 0b111
            immediate = instruction & 0b1111111
            rf.setValue(dest_register, immediate)

        elif opcode == 0b00011:  # Move Register - Type C
            dest_register = (instruction >> 8) & 0b111
            src_register = instruction & 0b111
            rf.setValue(dest_register, rf.getValue(src_register))

        # Rest of the ISA instructions...

        elif opcode == 0b11010:  # Halt - Type F
            return True, pc

        return False, pc + 1

def initializeMemoryFromInput(mem):
    print("Enter binary data for memory (empty line to finish):")
    all_lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        all_lines.append(line.strip())
    
    for i, line in enumerate(all_lines):
        mem.storeData(i, int(line, 2))




def main():
    mem = Memory()
    initializeMemoryFromInput(mem)
    
    pc = 0
    halted = False
    rf = RegisterFile()
    
    while not halted and pc < len(mem.data):
        instruction = mem.fetchData(pc)
        halted, new_pc = ExecutionEngine.execute(instruction, rf, pc)

        sys.stdout.write(format(pc, '07b') + ' ' * 8)
        rf.dump()

        pc = new_pc

    mem.dump()

if __name__ == '__main__':
    main()
