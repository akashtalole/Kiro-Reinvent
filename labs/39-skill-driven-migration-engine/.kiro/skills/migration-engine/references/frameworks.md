# Framework detection and scanners

| Source | Detect by | Discovery approach |
| --- | --- | --- |
| Laravel (Eloquent) | `artisan`, `composer.json` requires `laravel/framework` | Token-scan classes extending `Illuminate\Database\Eloquent\Model`; read `$fillable`, `$hidden`, `$casts`, relationship methods |
| Symfony (Doctrine) | `symfony/framework-bundle` | `#[ORM\Entity]` attributes and `*.orm.xml` mappings |
| Django | `manage.py`, `settings.py` | `models.Model` subclasses via `ast` |
| Rails | `Gemfile` with `rails` | `ApplicationRecord` subclasses, `db/schema.rb` |
| .NET Framework | `*.csproj` with `TargetFrameworkVersion` | EF `DbContext`/`DbSet<>` via Roslyn |

Scanners must **read source as text/tokens and never execute the target code**, emit one JSON manifest with `models[]` and `flags[]`, and flag ambiguity (e.g. runtime-built `$fillable`) instead of guessing.

To add a framework: add a detection row here and a `references/<framework>-to-<target>.md` guide. The change is additive.
