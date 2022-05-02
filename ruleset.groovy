// For a complete list of rules, see:
// https://codenarc.github.io/CodeNarc/codenarc-rule-index.html

ruleset {
  ruleset('rulesets/basic.xml') {}
  ruleset('rulesets/braces.xml') {}
  ruleset('rulesets/comments.xml') {
    ClassJavadoc(enabled: false)
  }
  ruleset('rulesets/convention.xml') {
    CompileStatic(enabled: false)
    NoDef(enabled: false)
    VariableTypeRequired(ignoreVariableNames: '_')
  }
  ruleset('rulesets/design.xml') {
    BuilderMethodWithSideEffects(enabled: false)
    Instanceof(enabled: false)
  }
  ruleset('rulesets/exceptions.xml') {}
  ruleset('rulesets/formatting.xml') {
    ClassEndsWithBlankLine(enabled: false)
    ClassStartsWithBlankLine(enabled: false)
    ConsecutiveBlankLines(enabled: false)
    Indentation(spacesPerIndentLevel: 2, enabled: true)
    LineLength(length: 90)
    SpaceAfterOpeningBrace(ignoreEmptyBlock: true)
    SpaceAroundMapEntryColon(characterAfterColonRegex: /\s/)
    SpaceBeforeClosingBrace(ignoreEmptyBlock: true)
  }
  ruleset('rulesets/generic.xml') {}
  ruleset('rulesets/groovyism.xml') {}
  ruleset('rulesets/imports.xml') {}
  ruleset('rulesets/naming.xml') {
    FactoryMethodName(enabled: false)
    VariableName(ignoreVariableNames: '_')
  }
  ruleset('rulesets/security.xml') {}
  ruleset('rulesets/size.xml') {
    // This rule causes all sorts of CodeNarc crashes since version 1.1. We should
    // consider re-enabling it in the future when those are ironed out.
    AbcMetric(enabled: false)
    CrapMetric(enabled: false)
    NestedBlockDepth(maxNestedBlockDepth: 8)
  }
  ruleset('rulesets/unnecessary.xml') {
    UnnecessaryGetter(ignoreMethodNames: 'isUnix')
    UnnecessaryReturnKeyword(enabled: false)
  }
  ruleset('rulesets/unused.xml') {
    UnusedVariable(ignoreVariableNames: '_')
  }
}
