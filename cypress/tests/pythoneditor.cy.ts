/*
 * Copyright 2018-2025 Elyra Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

describe('Python Editor tests', () => {
  before(() => {
    cy.resetJupyterLab();
    cy.bootstrapFile('helloworld.py'); // load python file used to check existing contents
  });

  after(() => {
    // delete files created for testing
    cy.deleteFile('untitled*.py');
    cy.deleteFile('helloworld.py'); // delete python file used for testing
  });

  // Python Editor Tests
  it('opens blank Python editor from launcher', () => {
    cy.createNewScriptEditor('Python');
    cy.get('.lm-TabBar-tab[data-type="document-title"]');
    cy.closeTab(-1);
  });

  // Flaky test: Missing expected items in the context menu
  it.skip('check Python editor tab right click content', () => {
    cy.createNewScriptEditor('Python');
    cy.checkRightClickTabContent('Python');
    cy.closeTab(-1);
  });

  it('close editor', () => {
    cy.createNewScriptEditor('Python');
    cy.closeTab(-1);
  });

  it('opens blank Python editor from menu', () => {
    cy.findByRole('menuitem', { name: /file/i }).click();
    cy.findByText(/^new$/i).click();

    cy.get(
      '[data-command="script-editor:create-new-python-editor"] > .lm-Menu-itemLabel'
    ).click();
    cy.closeTab(-1);
  });

  it('opens blank Python editor from file explorer context menu', () => {
    cy.get('.jp-FileBrowser').should('be.visible');
    cy.get('.jp-DirListing-content').rightclick();
    cy.get('.lm-Menu').contains('New Python Editor').click();
    cy.closeTab(-1);
  });

  it('check toolbar and its content for Python file', () => {
    cy.createNewScriptEditor('Python');
    cy.checkScriptEditorToolbarContent();
    cy.closeTab(-1);
  });

  it('check kernel dropdown has Python option', () => {
    cy.createNewScriptEditor('Python');
    cy.get('.elyra-ScriptEditor .jp-Toolbar select > option[value*=python]');
    cy.closeTab(-1);
  });

  // check for new output console and scroll up/down buttons
  it('opens new output console', () => {
    cy.openHelloWorld('py');
    clickRunButton();
    cy.get('[id=tab-ScriptEditor-output]').should(
      'have.text',
      'Console Output'
    );
    cy.get('button[title="Top"]').should('be.visible');
    cy.get('button[title="Bottom"]').should('be.visible');

    //close console tab
    cy.closeTab(-1);

    // Close editor tab
    cy.closeTab(-1);
  });

  it('open Python file with expected content', () => {
    cy.openFileAndCheckContent('py');
    cy.closeTab(-1);
  });

  // TODO: Investigate CI failures commented below
  // check for expected output on running a valid code
  // it('checks for valid output', () => {
  //   cy.openHelloWorld('py');
  //   clickRunButton();
  //   cy.wait(1000);
  //   cy.get('.elyra-ScriptEditor-OutputArea-output').should(
  //     'have.text',
  //     'Hello Elyra\n'
  //   );

  //   //close console tab
  //   cy.closeTab(-1);

  //   // Close editor tab
  //   cy.closeTab(-1);
  // });

  // check for error message running an invalid code
  // it('checks for Error message', () => {
  //   cy.createNewScriptEditor('Python');
  //   cy.wait(1000);

  //   // Add some code with syntax error to the editor (wait code editor to load)
  //   cy.get('.CodeMirror-lines')
  //     .first()
  //     .should('be.visible')
  //     .type('print"test"');

  //   cy.wait(500);
  //   cy.dismissAssistant('scripteditor');
  //   clickRunButton();
  //   cy.findByText(/Error : SyntaxError/i).should('be.visible');

  //   //close console tab
  //   cy.closeTab(-1);

  //   // Close editor tab
  //   cy.closeTab(-1);

  //   // Dismiss save your work dialog by discarding changes
  //   cy.get('button.jp-mod-warn').click();
  // });
});

// ------------------------------
// ----- Utility Functions
// ------------------------------

// Click Run button
const clickRunButton = (): void => {
  cy.get('jp-button.elyra-ScriptEditor-Run').click();
};
