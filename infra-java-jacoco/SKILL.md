---
name: infra-java-jacoco
description: 为 Java Maven 项目添加 JaCoCo 单元测试覆盖率配置。自动在 pom.xml 中添加 maven-surefire-plugin 和 jacoco-maven-plugin，并创建基础的 MyTest.java 测试文件。
---

# 为 Java Maven 项目添加 JaCoCo 配置

## 适用场景

当以下情况时使用此 skill：

- Java Maven 项目需要添加单元测试覆盖率统计
- pom.xml 中缺少 JaCoCo 相关配置
- 需要创建基础的测试类文件

## 执行步骤

### 1. 检查项目状态

首先确认：
- 项目是 Maven 项目（存在 pom.xml）
- 当前分支状态
- 是否已有 JaCoCo 配置

### 2. 修改 pom.xml

在 `<build><plugins>` 部分添加以下插件配置：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.5</version>
    <configuration>
        <skipTests>false</skipTests>
        <argLine>@{argLine} -Dfile.encoding=UTF-8</argLine>
    </configuration>
</plugin>

<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.7</version>
    <executions>
        <execution>
            <id>jacoco-initialize</id>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>jacoco-site</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
            <configuration>
                <dataFile>target/jacoco.exec</dataFile>
                <outputDirectory>target/jacoco-ut</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```

**注意**：如果 pom.xml 中已有 maven-surefire-plugin 配置，需要替换为上述配置。

### 3. 创建基础测试类

在 `src/test/java/` 目录下创建 `MyTest.java`：

```java
import org.junit.Test;

public class MyTest {
    @Test
    public void test(){

    }
}
```

### 4. 验证配置

运行以下命令验证配置：
```bash
mvn test
```

成功后会在 `target/jacoco-ut` 目录生成覆盖率报告。

## 配置说明

- **maven-surefire-plugin 3.2.5**：配置测试运行插件，`skipTests=false` 确保测试执行
- **jacoco-maven-plugin 0.8.7**：配置 JaCoCo 覆盖率插件
  - `prepare-agent`：准备 JaCoCo agent
  - `report`：在 test 阶段生成覆盖率报告
  - 报告输出目录：`target/jacoco-ut`

## 注意事项

1. 在修改 pom.xml 之前，建议先调用 `specBeforeEditFile` 记录修改前快照
2. 修改完成后，调用 `specAfterEditFile` 记录修改后快照
3. 如果项目是多模块项目（父 POM packaging=pom），需要修改子模块的 pom.xml
4. 提交信息建议：`"添加 JaCoCo 依赖配置和基础测试类"`

## 快速使用

直接告诉 Claude："使用 add-jacoco skill 为当前项目添加 JaCoCo 配置"
