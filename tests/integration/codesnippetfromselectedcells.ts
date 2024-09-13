/*
 * Copyright 2018-2023 Elyra Authors
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

describe('Code snippet from cells tests', () => {
  beforeEach(() => {
    cy.resetJupyterLab();

    // Create new python notebook
    cy.get(
      '.jp-LauncherCard[data-category="Notebook"][title="Python 3 (ipykernel)"]'
    ).click();

    cy.wait(2000);
  });

  it('test empty cell', () => {
    cy.get('.jp-Notebook', { timeout: 10000 }).should('have.length', 1);
    cy.get('.jp-Cell').first().rightclick();

    cy.wait(2000);

    cy.get(
      'li.lm-Menu-item[data-command="codesnippet:save-as-snippet"]'
    ).should('have.class', 'lm-mod-disabled');
  });

  // Depends on https://issues.redhat.com/browse/RHOAIENG-12851
  it.skip('test 1 cell', () => {
    // Create new cell
    cy.get(
      '.jp-NotebookPanel-toolbar > div:nth-child(2) > button:nth-child(1)'
    ).click();

    cy.wait(2000);

    populateCells();

    cy.get('.jp-Notebook', { timeout: 10000 }).should('have.length', 1);
    cy.get('.jp-Cell').first().rightclick();

    cy.wait(2000);

    cy.get(
      'li.lm-Menu-item[data-command="codesnippet:save-as-snippet"]'
    ).click();

    cy.wait(2000);

    // Verify snippet editor contents
    cy.get('span[role="presentation"]:visible').should(
      'have.text',
      'print("test")'
    );
  });

  // Depends on https://issues.redhat.com/browse/RHOAIENG-12851
  it.skip('test 2 cells', () => {
    // Create new cells
    cy.get(
      '.jp-NotebookPanel-toolbar > div:nth-child(2) > button:nth-child(1)'
    ).click();

    cy.wait(2000);

    populateCells();

    // Select all cells
    cy.get(
      ':nth-child(1) > .jp-Cell-inputWrapper > .jp-InputArea > .jp-InputPrompt'
    )
      .first()
      .click({
        shiftKey: true
      });

    cy.get('div.lm-Widget.lm-Widget.jp-InputPrompt.jp-InputArea-prompt:visible')
      .first()
      .rightclick({
        force: true
      });

    cy.wait(2000);

    cy.get(
      'li.lm-Menu-item[data-command="codesnippet:save-as-snippet"]'
    ).click();

    cy.wait(2000);

    // Verify snippet editor contents
    cy.get(
      '.elyra-form-code > .CodeMirror > .CodeMirror-scroll span[role="presentation"]:contains("test")'
    ).should('have.length', 2);
  });
});

// ------------------------------
// ----- Utility Functions
// ------------------------------

// Populate cells
const populateCells = (): void => {
  cy.get('.jp-Cell').each(($cell) => {
    cy.wrap($cell).click();
    cy.wrap($cell).should('have.class', 'jp-mod-selected');
    cy.wrap($cell)
      .find('.jp-InputArea')
      .click()
      .type('print("test")', { delay: 100 });
  });
};
