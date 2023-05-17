import sys
dictionary_registers = {'R0': '000', 'R1': '001', 'R2': '010', 'R3': '011', 'R4': '100', 'R5': '101', 'R6': '110', 'FLAGS': '111'}
dictionary_functions = {'add': '00000', 'sub': '00001', 'ld': '00100', 'st': '00101', 'mul': '00110', 'div': '00111',
                        'rs': '01000', 'ls': '01001', 'xor': '01010', 'or': '01011', 'and': '01100', 'not': '01101',
                        'cmp': '01110', 'jmp': '01111', 'jlt': '11100', 'jgt': '11101', 'je': '11111', 'hlt': '11010'}
typeA = ['add', 'sub', 'mul', 'and', 'or', 'xor']
typeB = ['rs', 'ls','mov']
typeC = ['div', 'not', 'cmp','mov']
typeD = ['ld', 'st', 'reg1']
typeE = ['jmp', 'jlt', 'jgt', 'je']
typeF = ['hlt']
def decimal_to_binary(a):
    a=str(a)
    k = a.strip('$')
    k = int(k)
    string = ''
    while k > 0:
        string += str(k % 2)
        k = k // 2

    for i in range(7 - len(string)):
        string += '0'
    m = ''
    for i in range(1, len(string) + 1):
        m += string[-i]
    return m


def assemble():
    variables = {}
    labels = {}
    instructions = []
    c=0
    
    # Read from stdin
    lines = sys.stdin.readlines()
    for line in lines:
        line=line.split()
        if line[0]=='var':
            c+=1
    for l in lines:
        lin=l.split()
        if lin[0]!='var':
            li=lines.index(l)
            break
    l=len(lines[li:])

    # Process each line of the input
    for line in lines:
        line_number=lines.index(line)
        if ':'in line:
            p=lines.index(line)
        line = line.strip()
        # Skip empty lines
        if not line:
            continue

        # Check if the line is a label
        if ':' in line:
            j=':'
            i=line.index(j)
            label = line[:i]
            if label in variables:
                raise SyntaxError(f"Error at line {line_number}: Label '{label}' cannot be used as a variable")
            elif label in labels:
                raise SyntaxError(f"Error at line {line_number}: Duplicate label '{label}'")
            else:
                labels[label] = p-c
                instructions.append(line[i+1:])
        else:
            instructions.append(line)

    # Check for missing hlt instruction
    if 'hlt'  not in instructions[-1]:
        raise SyntaxError("Error: Missing hlt instruction at the end of the program")

    # Process each instruction
    binary_instructions = []
    for line_number, instruction in enumerate(instructions, start=1):
        try:
            binary_string = process_instruction(instruction, line_number, variables, labels,instructions,l)
            binary_instructions.append(binary_string)
        except SyntaxError as e:
            print(str(e))
            return

    # Write to stdout
    print('\n'.join(binary_instructions))
def process_instruction(instruction, line_number, variables, labels,instructions,l):
    binary_string = ''
    k = instruction.split()
    
    k[len(k) - 1] = k[len(k) - 1].strip()

    opcode = k
    opcode = k[0]
    if opcode=="var":
        if k[-1] in variables:
            raise SyntaxError(f"Error at line {line_number}: variable already defined")
        variables.update({k[-1]:l+line_number-1})
    elif opcode=='mov':
        pass
    elif opcode not in dictionary_functions:
        raise SyntaxError(f"Error at line {line_number}: Invalid opcode '{opcode}'")    
    if opcode in typeA:
        if len(k) != 4:
            raise SyntaxError(f"Error at line {line_number}: Incorrect number of operands for opcode '{opcode}'")

        binary_string += dictionary_functions[opcode]
        binary_string += '00'

        for i in range(1, 4):
            if k[i] not in dictionary_registers:
                raise SyntaxError(f"Error at line {line_number}: Invalid register '{k[i]}'")
            elif k[i] == "FLAGS":
                raise SyntaxError(f"Error at line {line_number}: Invalid use of flag")
            binary_string += dictionary_registers[k[i]]

    elif opcode in typeB and '$'in instruction:
        if len(k) != 3:
            raise SyntaxError(f"Error at line {line_number}: Incorrect number of operands for opcode '{opcode}'")
        if k[0]!='mov':
            binary_string += dictionary_functions[opcode]
        else:
            binary_string+='00010'
        binary_string+='0'   
        if k[1] not in dictionary_registers:
            raise SyntaxError(f"Error at line {line_number}: Invalid register '{k[1]}'")
        elif k[1]=="FLAGS":
            raise SyntaxError(f"Error at line {line_number}: Invalid use of flag")
        binary_string += dictionary_registers[k[1]]

        if not k[2][-1].isdigit():
            raise SyntaxError(f"Error at line {line_number}: Invalid immediate value '{k[2]}'")
        immediate = int(k[2][-1])

        if immediate > 127:
            raise SyntaxError(f"Error at line {line_number}: Immediate value '{immediate}' exceeds 7-bit limit")
        binary_string += decimal_to_binary(k[2])


    elif opcode in typeC:
        if len(k) != 3:
            raise SyntaxError(f"Error at line {line_number}: Incorrect number of operands for opcode '{opcode}'")
        if k[0]!='mov':
            binary_string += dictionary_functions[opcode]
        else:
            binary_string+='00011'
        binary_string += '00000'
        for i in range(1, 3):
            if k[i] not in dictionary_registers:
                raise SyntaxError(f"Error at line {line_number}: Invalid register '{k[i]}'")
            elif k[1]=="FLAGS"and k[0]!="mov":
                raise SyntaxError(f"Error at line {line_number}: Invalid use of flag")
            binary_string += dictionary_registers[k[i]]
    elif opcode in typeD:
        if len(k) != 3:
            raise SyntaxError(f"Error at line {line_number}: Incorrect number of operands for opcode '{opcode}'")

        binary_string += dictionary_functions[opcode]
        binary_string+='0'
        if k[1] not in dictionary_registers:
            raise SyntaxError(f"Error at line {line_number}: Invalid register '{k[1]}'")
        elif k[1]=="FLAGS":
            raise SyntaxError(f"Error at line {line_number}: Invalid use of flag")
        binary_string += dictionary_registers[k[1]]

        if k[2] not in variables:
            raise SyntaxError(f"Error at line {line_number}: Undefined variable '{k[2]}'")
        binary_string += decimal_to_binary(variables[k[2]])
    elif opcode in typeE:
        if len(k) != 2:
            raise SyntaxError(f"Error at line {line_number}: Incorrect number of operands for opcode '{opcode}'")

        binary_string += dictionary_functions[opcode]
        binary_string+='0000'
        if k[1] not in labels:
            raise SyntaxError(f"Error at line {line_number}: Undefined label '{k[1]}'")
        binary_string += decimal_to_binary(labels[k[1]])

    elif opcode in typeF:
        if len(k) != 1:
            raise SyntaxError(f"Error at line {line_number}: Incorrect number of operands for opcode '{opcode}'")

        binary_string += dictionary_functions[opcode]
        binary_string += '00000000000'

    return binary_string

assemble()