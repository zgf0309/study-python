# 标注查询语句对象的类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Select
# 构造 ORM 查询语句。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import func, select
# 表示当前 CRUD 使用的数据库会话类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import Session

# models: 菜单、用户等 ORM 模型定义模块。
# schemas: 菜单相关的数据传输结构模块。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import models, schemas


# 中文注释：定义函数 list_menus，封装一段可复用的业务逻辑。
def list_menus(
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    db: Session,
    # 中文注释：执行当前代码行对应的业务逻辑。
    *,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    name: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    status: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page: int = 0,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page_size: int = 10,
# 中文注释：执行当前代码行对应的业务逻辑。
) -> list[models.Menu]:
    # 中文注释：设置变量或字段 statement: Select[tuple[models.Menu]] 的值，供后续逻辑使用。
    statement: Select[tuple[models.Menu]] = select(models.Menu)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if name:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.where(models.Menu.name.ilike(f'%{name}%'))

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        statement = statement.where(models.Menu.status == status)

    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = statement.order_by(models.Menu.sort.asc(), models.Menu.id.asc())

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if page >= 1 and page_size > 0:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.offset((page - 1) * page_size).limit(page_size)

    # 中文注释：返回当前函数处理后的结果。
    return list(db.scalars(statement))


# 中文注释：定义函数 count_menus，封装一段可复用的业务逻辑。
def count_menus(
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    db: Session,
    # 中文注释：执行当前代码行对应的业务逻辑。
    *,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    name: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    status: str | None = None,
# 中文注释：执行当前代码行对应的业务逻辑。
) -> int:
    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = select(func.count()).select_from(models.Menu)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if name:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.where(models.Menu.name.ilike(f'%{name}%'))

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        statement = statement.where(models.Menu.status == status)

    # 中文注释：返回当前函数处理后的结果。
    return int(db.scalar(statement) or 0)


# 中文注释：定义函数 get_menu，封装一段可复用的业务逻辑。
def get_menu(db: Session, menu_id: int) -> models.Menu | None:
    # 中文注释：返回当前函数处理后的结果。
    return db.get(models.Menu, menu_id)


# 中文注释：定义函数 create_menu，封装一段可复用的业务逻辑。
def create_menu(db: Session, payload: schemas.MenuCreate) -> models.Menu:
    # 中文注释：设置变量或字段 menu 的值，供后续逻辑使用。
    menu = models.Menu(**payload.model_dump())
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.add(menu)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(menu)
    # 中文注释：返回当前函数处理后的结果。
    return menu


# 中文注释：定义函数 update_menu，封装一段可复用的业务逻辑。
def update_menu(db: Session, payload: schemas.MenuUpdate) -> models.Menu:
    # 中文注释：设置变量或字段 menu 的值，供后续逻辑使用。
    menu = db.get(models.Menu, payload.id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not menu:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('Menu not found')
    # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
    for key, value in payload.model_dump().items():
        # 主键 id 只用于定位记录，不应在更新时再次写回，避免误改主键导致关联数据异常。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if key == 'id':
            # 中文注释：跳过本轮循环，继续处理下一项。
            continue
        # 中文注释：调用函数或方法，执行对应的业务处理。
        setattr(menu, key, value)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(menu)
    # 中文注释：返回当前函数处理后的结果。
    return menu


# 中文注释：定义函数 delete_menu，封装一段可复用的业务逻辑。
def delete_menu(db: Session, menu_id: int) -> bool:
    # 中文注释：设置变量或字段 menu 的值，供后续逻辑使用。
    menu = db.get(models.Menu, menu_id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not menu:
        # 中文注释：返回当前函数处理后的结果。
        return False
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.delete(menu)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：返回当前函数处理后的结果。
    return True
