/*
 * Copyright (c) 2026 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */

import java.io.Serializable;

/**
 * Stub for the implicit base class of Jenkins Pipeline scripts.
 *
 * Jenkins compiles the {@code Jenkinsfile} into a Groovy script class named
 * {@code WorkflowScript} (derived from
 * {@code org.jenkinsci.plugins.workflow.cps.CpsScript}) at runtime. Hence, any
 * {@code Jenkinsfile} that includes classes which subclass {@class WorkflowScript} will
 * give CodeNarc unresolved class errors under Groovy 4 and later.
 *
 * This stub class gives us a {@code WorkflowScript} name to put in the classpath to
 * satisfy type resolution for CodeNarc. The class itself is never executed.
 */
public class WorkflowScript extends groovy.lang.Script implements Serializable {
    @Override
    public Object run() {
        throw new RuntimeException("Executing this class is not supported");
    }
}
