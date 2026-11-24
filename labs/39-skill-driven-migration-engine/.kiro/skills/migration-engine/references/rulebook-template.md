# RULEBOOK.md — <source> → <target>

Each rule is mechanical and traceable. Format:

## R-<NNN> <short name>
- **Source pattern:** e.g. Eloquent `hasMany(Chapter::class)`
- **Target pattern:** e.g. JPA `@OneToMany(mappedBy = "book")`
- **Manifest fields used:** `relationships[].type`, `relationships[].related`
- **Example:** before / after snippet
- **Added in phase / because of:** harness case id or file that exposed the gap

Starter rules (PHP/Laravel → Java/Spring Boot):
- R-001 namespace → package
- R-002 Eloquent model → `@Entity`; `$table` → `@Table(name=…)`
- R-003 `hasMany` / `belongsTo` → `@OneToMany` / `@ManyToOne`
- R-004 `$hidden` attributes → `@JsonIgnore`
- R-005 `$casts` → Java types (`'boolean'`→`boolean`, `'datetime'`→`Instant`, `'array'`→JSON converter)
- R-006 query scopes → Spring Data repository methods
- R-007 routes → `@RestController` mappings; middleware → filters; form requests → validated DTOs
