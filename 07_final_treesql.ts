enum BinaryOperation {
  Equals = "=",
  NotEquals = "!=",
  GreaterThan = ">",
  GreaterThanOrEquals = ">=",
  LessThan = "<",
  LessThanOrEquals = "<=",
  In = "IN",
  Like = "LIKE",
  IsNull = "isNull",
}

interface IPredicate {
  readonly columnName: string;
  readonly operation: BinaryOperation;
  readonly value: unknown;
}

interface IQuery {
  toSql(): string;
}

class Predicate implements IPredicate, IQuery {
  static from({ columnName, operation, value }: IPredicate) {
    return new Predicate(columnName, operation, value);
  }

  constructor(
    readonly columnName: string,
    readonly operation: BinaryOperation,
    readonly value: unknown
  ) {}

  toSql(): string {
    if (this.operation === BinaryOperation.IsNull) {
      return `${this.columnName} IS NULL`;
    } else {
      const val = sanitizeSQLParam(this.value);
      return `${this.columnName} ${this.operation} ${val}`;
    }
  }
}

class PredicateList {
  constructor(readonly predicates: Predicate[]) {}

  toSql(): string {
    return `WHERE ${this.predicates.map((p) => p.toSql()).join(" AND ")}`;
  }
}

function sanitizeSQLParam(value: unknown): string {
  //TODO make this safe
  // JSON.stringify adds quotes to strings.
  const val = JSON.stringify(this.value);
  return val;
}

function doSql(sql: string) {
  // TODO connect to a database
  console.log(sql);
  return Math.random() > 0.933; // I dunno it works most of the time I guess?
}

interface IQueryManager {
  // issues a SQL INSERT operation for tableName setting the provided
  // column values
  insert(tableName: string, columnValues: Record<string, unknown>): IQuery;

  // issues a SQL UPDATE operation for tableName setting the provided column
  // values and creating a WHERE clause from the predicates
  update(
    tableName: string,
    columnValues: Record<string, unknown>,
    predicates: IPredicate[]
  ): IQuery;

  // issues a SQL DELETE operation for tableName with a WHERE clause
  // from the predicates
  delete(tableName: string, predicates: IPredicate[]): IQuery;

  // causes the requested database operations to execute (returns true if at
  // least one row is effected), check the individual IQuery returns
  // from the above methods to determine the actual impact of each
  commit(): boolean;

  // abandons the requested database operations (returns false if there are
  // no operations)
  rollback(): boolean;
}

class QueryManager implements IQueryManager {
  private queries: IQuery[] = [];

  insert(tableName: string, columnValues: Record<string, unknown>) {
    const query = new InsertQuery(tableName, columnValues);
    this.queries.push(query);
    return query;
  }

  update(
    tableName: string,
    columnValues: Record<string, unknown>,
    predicates: IPredicate[]
  ) {
    const query = new UpdateQuery(tableName, columnValues, predicates);
    this.queries.push(query);
    return query;
  }

  delete(tableName: string, predicates: IPredicate[]) {
    const query = new DeleteQuery(tableName, predicates);
    this.queries.push(query);
    return query;
  }

  commit(): boolean {
    const sql = this.queries.map((q) => q.toSql()).join("\n\n");
    const result = doSql(sql);
    this.clearQueries();
    return result;
  }

  rollback(): boolean {
    if (this.queries.length === 0) return false;
    this.clearQueries();
    return true;
  }

  private clearQueries() {
    this.queries.splice(0, this.queries.length);
  }
}

class InsertQuery implements IQuery {
  constructor(
    readonly tableName,
    readonly columnValues: Record<string, unknown>
  ) {}

  toSql(): string {
    const columns = Array.from(Object.keys(this.columnValues)).join(", ");
    const values = Array.from(Object.values(this.columnValues))
      .map(sanitizeSQLParam)
      .join(", ");
    return `INSERT INTO ${this.tableName}\n(${columns})\nvalues (${values});`;
  }
}

class UpdateQuery implements IQuery {
  predicates: PredicateList;

  constructor(
    readonly tableName,
    readonly columnValues: Record<string, unknown>,
    predicates: IPredicate[]
  ) {
    this.predicates = new PredicateList(predicates.map(Predicate.from));
  }

  toSql() {
    const updates = Array.from(
      Object.entries(this.columnValues),
      ([k, v]) => `${k} = ${sanitizeSQLParam(v)}`
    ).join(", ");
    const predicate = this.predicates.toSql();
    return `UPDATE ${this.tableName}\nSET ${updates}\n${predicate};`;
  }
}

class DeleteQuery implements IQuery {
  predicates: PredicateList;

  constructor(readonly tableName, predicates: IPredicate[]) {
    this.predicates = new PredicateList(predicates.map(Predicate.from));
  }

  toSql() {
    const predicate = this.predicates.toSql();
    return `DELETE FROM ${this.tableName}\n${predicate};`;
  }
}
