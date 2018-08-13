// For a complete list of rules, see:
// http://codenarc.sourceforge.net/codenarc-rule-index.html

ruleset {
  ruleset('rulesets/basic.xml') {}
  ruleset('rulesets/braces.xml') {}
  ruleset('rulesets/convention.xml') {
    NoDef(enabled: false)
    VariableTypeRequired(ignoreVariableNames: '_')
  }
  ruleset('rulesets/design.xml') {
    Instanceof(enabled: false)
  }
  ruleset('rulesets/exceptions.xml') {}
  ruleset('rulesets/formatting.xml') {
    ClassJavadoc(enabled: false)
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
    NestedBlockDepth(maxNestedBlockDepth: 8)
  }
  ruleset('rulesets/unnecessary.xml') {
    UnnecessaryReturnKeyword(enabled: false)
  }
  ruleset('rulesets/unused.xml') {
    UnusedVariable(ignoreVariableNames: '_')
  }
}
