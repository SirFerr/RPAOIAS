from demo_program import assemble_and_run_demo

if __name__ == "__main__":
    # Example: sum of [5, -2, 10, 7] = 122
    program, state = assemble_and_run_demo([5, -2, 112, 7], trace=True)
    print("\n--- Machine code (hex) ---")
    print(" ".join(f"{b:02X}" for b in program))
    print("\n--- Final CPU state ---")
    print(state)
