## Dataclasses

Чаще всего в программах на Python для передачи данных пользуются
словарями `dict` или функцией `namedtuple`.

`dict` не позволяет понять, есть ли такой аргумент у вызываемой функции или
нет — приходится лезть в сигнатуру метода. 

С `namedtuple` есть проблема с производительностью: у них медленные операции чтения,
доступа к вложенным объектам и выполнения стандартных функций.

### Преимущества `dataclasses`
- [Они быстрее, чем `namedtuple`, и проще в обращении, чем `dict`](https://medium.com/@jacktator/dataclass-vs-namedtuple-vs-object-for-performance-optimization-in-python-691e234253b9);
- **обязательное указание типа данных для каждого атрибута в
`dataclass`**: это упрощает отлов ошибок в IDE и позволяет применять
инструменты статического анализа кода, например, `mypy`;
- `dataclass` можно делать неизменяемыми — immutable;
- можно использовать слоты в `dataclass` (но только при условии, что у них нет атрибутов, которые заданы через field).
- когда вы применяете `dataclass`, то можете получать подсказки в IDE с именами атрибутов у объектов



```python
import uuid
from dataclasses import dataclass, field


@dataclass
class Movie:
    title: str
    description: str
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class MovieWithoutField:
    __slots__ = ('title', 'description')
    title: str
    description: str
```
