def jenkinsImportLibraryName = '_'

ruleset {
  ruleset('rulesets/basic.xml') {}
  ruleset('rulesets/braces.xml') {}
  ruleset('rulesets/convention.xml') {
    NoDef(enabled: false)
  }
  ruleset('rulesets/design.xml') {
    Instanceof(enabled: false)
  }
  ruleset('rulesets/dry.xml') {
    DuplicateMapLiteral(enabled: false)
    DuplicateStringLiteral(enabled: false)
  }
  ruleset('rulesets/exceptions.xml') {}
  ruleset('rulesets/formatting.xml') {
    ClassJavadoc(enabled: false)
    ConsecutiveBlankLines(enabled: false)
    SpaceAfterOpeningBrace(ignoreEmptyBlock: true)
    SpaceAroundMapEntryColon(characterAfterColonRegex: /\s/)
    SpaceBeforeClosingBrace(ignoreEmptyBlock: true)
  }
  ruleset('rulesets/generic.xml') {}
  ruleset('rulesets/groovyism.xml') {}
  ruleset('rulesets/imports.xml') {}
  ruleset('rulesets/naming.xml') {
    FactoryMethodName(enabled: false)
    VariableName(ignoreVariableNames: jenkinsImportLibraryName)
  }
  ruleset('rulesets/security.xml') {}
  ruleset('rulesets/size.xml') {}
  ruleset('rulesets/unnecessary.xml') {
    UnnecessaryReturnKeyword(enabled: false)
  }
  ruleset('rulesets/unused.xml') {
    UnusedVariable(ignoreVariableNames: jenkinsImportLibraryName)
  }
}
