# Skill: Language-Specific Rules

Reusable reference for language-specific pitfalls, idioms, and best practices. Each agent should apply the relevant section based on the detected or specified language.

## Language Detection

If the user specifies a language, use that section. If set to "unspecified" or "Auto-detect", infer the language from:
1. File extension patterns in the code (`.py`, `.js`, `.ts`, `.go`, etc.)
2. Syntax markers: `def`/`import` → Python; `function`/`const`/`let` → JS/TS; `func`/`package` → Go; `fn`/`let mut` → Rust
3. Framework imports: `django`, `flask` → Python web; `express`, `react` → JS/TS

---

## Python

### Security Pitfalls
- `eval()` / `exec()` on user input → command injection
- `pickle.loads()` on untrusted data → arbitrary code execution
- `yaml.load()` without `Loader=yaml.SafeLoader` → code execution
- `subprocess.shell=True` with user input → command injection
- `os.path.join()` doesn't protect against `../` traversal — use `pathlib.Path.resolve()`
- `assert` statements are disabled with `python -O` — never use for security checks
- `random` module is not cryptographically secure — use `secrets` for tokens

### Bug Pitfalls
- Mutable default arguments: `def f(x=[])` — `[]` is shared across all calls
- Late binding closures in loops: `[lambda: i for i in range(3)]` all return 2
- `is` vs `==`: `is` tests identity (same object), `==` tests equality — never use `is` for value comparison except `is None`
- Generator exhaustion: generators can only be iterated once
- `dict.keys()` returns a view, not a copy — mutating the dict while iterating raises RuntimeError
- `float` comparison with `==` — use `math.isclose()` or tolerance-based comparison
- Catching `except Exception` swallows `KeyboardInterrupt`, `SystemExit` — prefer specific types

### Quality Idioms
- `for i in range(len(x))` → prefer `enumerate(x)` or iterate directly
- `if x == True` → `if x`; `if x == False` → `if not x`; `if x == None` → `if x is None`
- `dict.get(key, default)` instead of `if key in dict: ... else: ...`
- `with open() as f:` instead of `f = open()` / `f.close()`
- `@dataclass` or `NamedTuple` instead of plain dicts for structured data
- `pathlib.Path` instead of `os.path` string manipulation
- `f"..."` over `"...".format(...)` or `%` formatting (Python 3.6+)
- `collections.defaultdict` or `dict.setdefault` over manual key existence check

### Performance
- String concatenation in a loop → `"".join(parts)`
- Repeated `in` checks on lists → convert to `set` for O(1) lookup
- `functools.lru_cache` for pure functions called with repeated arguments
- List comprehensions are faster than equivalent `for` + `append()` loops
- Avoid `global` variables — they prevent optimization and complicate testing

---

## JavaScript / TypeScript

### Security Pitfalls
- `innerHTML` / `outerHTML` / `document.write` with user data → XSS
- `eval()` / `new Function()` with user input → code injection
- `dangerouslySetInnerHTML` in React without sanitization → XSS
- `JSON.parse()` on untrusted data without try/catch → crashes, DoS
- Prototype pollution: `obj[userKey] = value` where `userKey` could be `__proto__`
- `window.location = userInput` → open redirect or `javascript:` URL

### Bug Pitfalls
- `==` performs type coercion — always use `===` for comparison
- `typeof null === 'object'` — check `x !== null && typeof x === 'object'`
- `NaN !== NaN` — use `Number.isNaN()` not `x === NaN`
- `async` functions return Promises — forgetting `await` causes silent failures
- Event listener `this` context is lost without `.bind()` or arrow function
- `var` is function-scoped and hoisted — use `const`/`let`
- Accessing `.length` on undefined crashes — check first or use optional chaining `?.`
- `Array.prototype.sort()` sorts lexicographically by default — pass a comparator for numbers

### TypeScript-Specific
- `any` disables type checking — prefer `unknown` with type narrowing
- Non-null assertion `!` suppresses type errors — prove non-null with a guard instead
- `as Type` casts bypass type safety — prefer type predicates or `unknown` → guard → use
- Enums create runtime objects — `const enum` or union types often preferred
- `interface` is extensible (declaration merging); `type` is not — choose deliberately

### Quality Idioms
- `arr.forEach` when `arr.map` / `arr.filter` / `arr.reduce` better expresses intent
- Optional chaining `?.` for safe property access on nullable values
- Nullish coalescing `??` instead of `||` when `0` or `""` are valid values
- Destructuring for cleaner parameter access: `const { name, age } = user`
- Template literals over string concatenation
- `Promise.all()` for parallel async operations instead of sequential `await`

---

## TypeScript (Additional)

### Type Safety Patterns
- Discriminated unions over optional fields for variant types
- `Record<K, V>` over index signatures `{ [key: string]: V }` when key type is known
- `Readonly<T>` and `ReadonlyArray<T>` for data that shouldn't be mutated
- `satisfies` operator (TS 4.9+) for type-safe object literals without widening
- Branded types for domain primitives (`type UserId = string & { readonly brand: 'UserId' }`)

---

## Java

### Security Pitfalls
- String-concatenated SQL queries → use `PreparedStatement`
- `Runtime.exec()` with string concatenation → command injection
- Deserializing untrusted `ObjectInputStream` → arbitrary code execution
- `XMLInputFactory` without disabling external entities → XXE

### Bug Pitfalls
- `==` compares references for objects — use `.equals()` for value comparison
- `NullPointerException` from uninitialized fields — use `Optional<T>` or initialize in constructor
- `ArrayList` iteration with `list.remove()` inside for loop → `ConcurrentModificationException`
- `int` overflow in expressions like `(a + b) / 2` → use `a + (b - a) / 2`
- `String.split()` silently discards trailing empty strings — use `split(regex, -1)` when needed
- `HashMap` is not thread-safe — use `ConcurrentHashMap` in concurrent contexts

### Quality Idioms
- `Optional` instead of returning `null` from methods
- `try-with-resources` instead of `finally` for `Closeable` resources
- `var` for local type inference (Java 10+) when type is obvious from right-hand side
- Records (Java 16+) for immutable data carriers instead of verbose POJOs
- Stream API instead of manual `for` loops for collection transformation

---

## Go

### Security Pitfalls
- `fmt.Sprintf` SQL queries → use `database/sql` with parameterized queries
- `os/exec` with shell interpolation → use `exec.Command` with separate args
- `path.Join()` doesn't clean `..` — use `filepath.Clean()` and validate

### Bug Pitfalls
- Ignoring returned `error` values — Go functions signal failure through error returns
- Closing over loop variables in goroutines: `go func() { fmt.Println(v) }()` captures last `v`
- Nil map assignment panics — initialize with `make(map[K]V)`
- Slice aliasing: `b := a[1:3]` shares underlying array — modifications affect both
- `defer` in a loop defers to function exit, not loop iteration end
- `time.Sleep` in tests is flaky — use channels or `sync.WaitGroup`

### Quality Idioms
- `errors.Is()` / `errors.As()` for error comparison instead of `err == ErrFoo`
- `%w` verb in `fmt.Errorf` for wrappable errors
- Table-driven tests with `t.Run()` for multiple test cases
- Context propagation: functions doing IO should accept `context.Context` as first param
- `sync.Once` for lazy initialization instead of mutex-guarded nil checks

---

## Rust

### Bug Pitfalls
- Integer overflow in debug mode panics; in release mode wraps silently — use checked arithmetic
- `unwrap()` / `expect()` panic on `None`/`Err` — use `?` or pattern matching in production code
- Cloning unnecessarily large data — consider borrowing or `Arc<T>`

### Quality Idioms
- `match` exhaustiveness — Rust compiler enforces it, but reviewers should check `_` catch-alls
- `impl From<X> for Y` for ergonomic type conversions
- `Iterator` adapters (`map`, `filter`, `flat_map`) over manual loops
- `?` operator for clean error propagation instead of nested `match`

---

## SQL

### Security Pitfalls
- String-concatenated queries from any language → parameterized queries only
- `SELECT *` in production queries → enumerate columns explicitly
- `EXECUTE` / `EXEC` with string-built SQL → stored procedures or parameterized

### Bug Pitfalls
- `NULL` comparisons: `x = NULL` is always false — use `IS NULL` / `IS NOT NULL`
- `OUTER JOIN` with `WHERE` clause filtering joined table → unintentionally becomes `INNER JOIN`
- Integer division: `5 / 2 = 2` in most databases — cast to float explicitly
- Missing `LIMIT` on user-driven queries → potential full table scan exposure

### Quality
- `SELECT *` makes schema changes silently break queries
- Unindexed `WHERE` columns on large tables → slow queries
- `ORDER BY` without deterministic tiebreaker → non-deterministic pagination

---

## Shell / Bash

### Security Pitfalls
- Unquoted variables: `rm $file` → word splitting allows `rm -rf /` if `$file` contains spaces
- `eval` on user input → arbitrary command execution
- Temporary files in `/tmp` without `mktemp` → symlink attacks

### Bug Pitfalls
- Unquoted `$@` vs `"$@"` — unquoted splits on whitespace
- `[ $x = "foo" ]` fails when `$x` is empty — use `[[ ]]` or quote: `[ "$x" = "foo" ]`
- `set -e` doesn't catch failures in pipelines — add `set -o pipefail`
- Exit code of last command in a pipeline is used — leftmost failures are hidden
