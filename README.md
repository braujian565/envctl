# envctl

> CLI tool to manage and switch between project environment variable sets safely.

---

## Installation

```bash
pip install envctl
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envctl
```

---

## Usage

```bash
# Initialize envctl in your project
envctl init

# Create a new environment set
envctl create staging

# Set a variable in an environment
envctl set staging DATABASE_URL=postgres://localhost/mydb

# List all environment sets
envctl list

# Switch to an environment
envctl use staging

# Show current active environment variables
envctl show
```

Environment variable sets are stored locally and never committed to version control by default. envctl automatically adds its config to your `.gitignore`.

---

## Why envctl?

Switching between `development`, `staging`, and `production` configs manually is error-prone. envctl lets you define named environment sets and switch between them with a single command — safely and consistently.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)