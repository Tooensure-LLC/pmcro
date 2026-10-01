# The design, layer by layer

Source: described by the owner in chat on 2026-10-01 as the design he always follows (he notes it resembles clean architecture). This file records his description; it is not an external standard.

| Layer (folder) | Piece | Rule |
| --- | --- | --- |
| Domain | `BaseEntity` (abstract) | `Guid Id = Guid.NewGuid()`. Every model inherits it, so every model has an Id and a random one by default. |
| Domain | `User : BaseEntity` | The only thing you write by hand. |
| Application | `IGenericRepository<T> where T : BaseEntity` | Get all, get by id, add, update, delete. Works for every T because every T has an Id. |
| Application | `IUnitOfWork` | `Repository<T>()` and one `SaveChangesAsync`. |
| Application | `IUserRepository : IGenericRepository<User>` | Empty unless the model needs a special feature. |
| Infrastructure | `GenericRepository<T>` | Implements the interface once, against the DbContext. |
| Infrastructure | `UserRepository : GenericRepository<User>, IUserRepository` | Empty unless special. |
| Infrastructure | `AppDbContext` | Registers every concrete `BaseEntity` automatically, so no DbSet per model. |
| Api | `GenericController<T>` | GET, GET by id, POST, PUT, DELETE. |
| Api | `UsersController : GenericController<User>` | One line. |

Object-oriented ideas in use: abstraction (interfaces), encapsulation (the DbContext hidden behind repositories), inheritance (every model from BaseEntity, every repository from the generic one) and polymorphism (one controller and repository serving any T).

## Choices the scaffold makes that the owner did not state

- Repositories do not save; the controller calls the unit of work once. (Chosen so several repositories can change together in one save.)
- POST ignores a client-supplied id and PUT takes the id from the route.
- Controller names add a plain "s" (`UsersController`); irregular plurals need a manual rename.
- The in-memory EF provider is a placeholder; production needs a real provider and migrations, not covered here.
- Single project with folders, not separate class libraries, so a small model can read it. Splitting into Domain, Application, Infrastructure and Api projects is a mechanical next step.

## Not covered

Validation, authentication, paging, filtering, soft delete, concurrency tokens, DTOs. Returning entities directly from controllers is acceptable for a scaffold, risky for a public API.
