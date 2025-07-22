"""
PostgreSQL MCP Server

This MCP server provides tools and resources for interacting with PostgreSQL databases.
It offers:
- Database schema resources
- SQL query execution tools
- Data analysis prompts
"""

import json
import os
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


# 创建MCP服务器实例
mcp = FastMCP("PostgreSQL Database Server")

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        raise Exception(f"数据库连接失败: {e}")


def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """执行SQL查询并返回结果"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:
                results = cur.fetchall()
                return [dict(row) for row in results]
            else:
                return []
    except psycopg2.Error as e:
        raise Exception(f"SQL查询执行失败: {e}")
    finally:
        if conn:
            conn.close()


# === 资源：数据库模式信息 ===


@mcp.resource("schema://tables")
def get_all_tables() -> str:
    """获取数据库中所有表的列表"""
    query = """
    SELECT 
        schemaname,
        tablename,
        tableowner
    FROM pg_tables 
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY schemaname, tablename;
    """

    try:
        results = execute_query(query)
        tables_info = {
            "database": DB_CONFIG["database"],
            "tables": results,
            "total_count": len(results),
        }
        return json.dumps(tables_info, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"获取表列表失败: {str(e)}"


@mcp.resource("schema://table/{table_name}")
def get_table_schema(table_name: str) -> str:
    """获取指定表的详细模式信息"""
    # 获取表结构
    schema_query = """
        SELECT 
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        c.character_maximum_length,
        c.numeric_precision,
        c.numeric_scale,
        pd.description
    FROM 
        information_schema.columns c
    LEFT JOIN 
        pg_catalog.pg_description pd
        ON pd.objsubid = c.ordinal_position
        AND pd.objoid = (
            SELECT 
                pc.oid 
            FROM 
                pg_catalog.pg_class pc
            JOIN 
                pg_catalog.pg_namespace pn 
                ON pn.oid = pc.relnamespace
            WHERE 
                pc.relname = 'api_request_log'
                AND pn.nspname = c.table_schema
        )
    WHERE 
        c.table_name = 'api_request_log'
        AND c.table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY 
        c.ordinal_position;

    """

    # 获取表的约束信息
    constraints_query = """
    SELECT 
        tc.constraint_name,
        tc.constraint_type,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = %s
    AND tc.table_schema NOT IN ('information_schema', 'pg_catalog');
    """

    # 获取表行数
    count_query = f"SELECT COUNT(*) as row_count FROM {table_name};"

    try:
        columns = execute_query(schema_query, (table_name,))
        constraints = execute_query(constraints_query, (table_name,))

        # 安全地执行行数查询
        try:
            row_count_result = execute_query(count_query)
            row_count = row_count_result[0]["row_count"] if row_count_result else 0
        except Exception:
            row_count = "无法获取"

        table_info = {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns,
            "constraints": constraints,
        }

        return json.dumps(table_info, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"获取表 '{table_name}' 的模式信息失败: {str(e)}"


@mcp.resource("schema://indexes/{table_name}")
def get_table_indexes(table_name: str) -> str:
    """获取指定表的索引信息"""
    query = """
    SELECT 
        indexname,
        indexdef
    FROM pg_indexes 
    WHERE tablename = %s
    AND schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY indexname;
    """

    try:
        results = execute_query(query, (table_name,))
        indexes_info = {
            "table_name": table_name,
            "indexes": results,
            "total_count": len(results),
        }
        return json.dumps(indexes_info, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"获取表 '{table_name}' 的索引信息失败: {str(e)}"


# === 工具：SQL查询执行 ===


@mcp.tool()
def execute_readonly_query(sql: str) -> str:
    """
    执行只读SQL查询

    Args:
        sql: 要执行的SQL查询语句（只支持SELECT语句）

    Returns:
        查询结果的JSON格式字符串
    """
    # 检查是否为只读查询
    sql_upper = sql.strip().upper()
    readonly_keywords = ["SELECT", "WITH"]
    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
    ]

    if not any(sql_upper.startswith(keyword) for keyword in readonly_keywords):
        return "错误: 只支持SELECT和WITH查询语句"

    if any(keyword in sql_upper for keyword in forbidden_keywords):
        return "错误: 不允许执行修改数据的SQL语句"

    try:
        results = execute_query(sql)

        return json.dumps(
            {
                "query": sql,
                "row_count": len(results),
                "results": results[:100],  # 限制返回前100行
                "truncated": len(results) > 100,
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        return f"查询执行失败: {str(e)}"


@mcp.tool()
def get_sample_data(table_name: str, limit: int = 10) -> str:
    """
    获取表的样本数据

    Args:
        table_name: 表名
        limit: 返回的行数限制（默认10行，最大100行）

    Returns:
        样本数据的JSON格式字符串
    """
    if limit > 100:
        limit = 100

    query = f"SELECT * FROM {table_name} LIMIT %s;"

    try:
        results = execute_query(query, (limit,))

        return json.dumps(
            {
                "table_name": table_name,
                "sample_size": len(results),
                "requested_limit": limit,
                "data": results,
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    except Exception as e:
        return f"获取表 '{table_name}' 样本数据失败: {str(e)}"


@mcp.tool()
def analyze_table_stats(table_name: str) -> str:
    """
    分析表的统计信息

    Args:
        table_name: 要分析的表名

    Returns:
        表统计信息的JSON格式字符串
    """
    # 获取表的基本统计信息
    stats_query = f"""
    SELECT 
        COUNT(*) as total_rows
    FROM {table_name};
    """

    # 获取数值列的统计信息
    numeric_stats_query = """
    SELECT 
        column_name,
        data_type
    FROM information_schema.columns 
    WHERE table_name = %s 
    AND data_type IN ('integer', 'bigint', 'decimal', 'numeric', 'real', 'double precision')
    AND table_schema NOT IN ('information_schema', 'pg_catalog');
    """

    try:
        # 基本统计
        basic_stats = execute_query(stats_query)

        # 数值列信息
        numeric_columns = execute_query(numeric_stats_query, (table_name,))

        # 为每个数值列计算统计信息
        column_stats = {}
        for col in numeric_columns:
            col_name = col["column_name"]
            try:
                col_query = f"""
                SELECT 
                    MIN({col_name}) as min_value,
                    MAX({col_name}) as max_value,
                    AVG({col_name}) as avg_value,
                    COUNT({col_name}) as non_null_count,
                    COUNT(*) - COUNT({col_name}) as null_count
                FROM {table_name};
                """
                col_result = execute_query(col_query)
                column_stats[col_name] = col_result[0] if col_result else {}
            except Exception:
                column_stats[col_name] = {"error": "无法计算统计信息"}

        analysis_result = {
            "table_name": table_name,
            "basic_stats": basic_stats[0] if basic_stats else {},
            "numeric_columns_stats": column_stats,
        }

        return json.dumps(analysis_result, indent=2, ensure_ascii=False, default=str)

    except Exception as e:
        return f"分析表 '{table_name}' 统计信息失败: {str(e)}"


# === 提示：常见数据分析任务 ===


@mcp.prompt(title="数据探索分析")
def data_exploration_prompt(table_name: str) -> str:
    """生成数据探索分析的提示"""
    return f"""
作为数据分析师，请帮我分析表 '{table_name}' 的数据。

请按以下步骤进行分析：

1. **表结构分析**
   - 查看表的模式信息，了解所有列的数据类型
   - 识别主键和外键约束
   - 检查索引配置

2. **数据质量检查**
   - 检查总行数和唯一行数
   - 识别是否有重复数据
   - 检查各列的空值情况
   - 分析数值列的分布（最小值、最大值、平均值）

3. **样本数据预览**
   - 查看前10行数据以了解数据格式
   - 识别异常值或不一致的数据

4. **提供分析建议**
   - 根据数据特征提出进一步分析的建议
   - 识别潜在的数据质量问题
   - 建议可能的分析角度

请使用可用的MCP工具来获取必要的信息并进行分析。
"""


@mcp.prompt(title="性能优化分析")
def performance_analysis_prompt(table_name: str) -> str:
    """生成性能优化分析的提示"""
    return f"""
作为数据库性能专家，请帮我分析表 '{table_name}' 的性能优化机会。

分析要点：

1. **表大小和增长趋势**
   - 当前表的行数
   - 表的存储空间使用情况

2. **索引分析**
   - 现有索引的配置
   - 识别缺失的索引机会
   - 检查是否有冗余或未使用的索引

3. **查询模式分析**
   - 基于表结构推断常见查询模式
   - 识别可能的性能瓶颈

4. **优化建议**
   - 索引优化建议
   - 查询优化建议
   - 表结构优化建议

请使用可用的工具来收集相关信息并提供具体的优化建议。
"""


@mcp.prompt(title="业务洞察分析")
def business_insights_prompt(
    table_name: str, business_context: str = ""
) -> list[base.Message]:
    """生成业务洞察分析的提示"""
    return [
        base.Message(
            role="user",
            content=f"""
作为业务分析师，请帮我从表 '{table_name}' 中挖掘业务洞察。

业务背景：{business_context if business_context else "请根据表结构和数据特征推断业务场景"}

分析目标：

1. **业务理解**
   - 基于表结构和字段名称理解业务场景
   - 识别关键业务指标

2. **趋势分析**
   - 如果有时间字段，分析时间趋势
   - 识别周期性模式

3. **分布分析**
   - 分析关键维度的数据分布
   - 识别异常值和特殊情况

4. **关联分析**
   - 分析不同字段之间的潜在关联
   - 识别业务规则和约束

5. **可行性建议**
   - 基于数据特征提出业务改进建议
   - 识别需要进一步收集的数据

请使用可用的工具来获取数据并提供具体的业务洞察。
""",
        )
    ]


@mcp.prompt(title="数据质量报告")
def data_quality_report_prompt(table_name: str) -> str:
    """生成数据质量报告的提示"""
    return f"""
请为表 '{table_name}' 生成详细的数据质量报告。

报告应包含以下内容：

## 1. 数据完整性检查
- 空值分析：每列的空值数量和比例
- 必填字段检查：关键业务字段的完整性
- 引用完整性：外键约束的满足情况

## 2. 数据一致性检查
- 重复数据检测
- 数据格式一致性
- 数值范围合理性检查

## 3. 数据准确性分析
- 异常值检测
- 数据类型匹配性
- 业务规则违反情况

## 4. 数据及时性评估
- 如有时间戳字段，检查数据更新频率
- 数据新鲜度分析

## 5. 改进建议
- 数据质量问题的优先级排序
- 具体的数据清理建议
- 预防措施推荐

请使用可用的MCP工具来收集数据并生成全面的质量报告。
"""


# 主程序入口
def main():
    """运行MCP服务器"""
    print("启动 PostgreSQL MCP 服务器...")
    print(
        f"数据库连接配置: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    # 测试数据库连接
    try:
        conn = get_db_connection()
        conn.close()
        print("数据库连接测试成功!")
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        print("请检查数据库配置和连接信息")

    # 启动MCP服务器
    mcp.run()


if __name__ == "__main__":
    main()
