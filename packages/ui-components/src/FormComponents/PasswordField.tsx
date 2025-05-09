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
import { FieldProps } from '@rjsf/utils';

import React from 'react';

import { viewIcon, viewOffIcon } from '..';

/**
 * React component to edit and display password fields. Adds a button to hide / show text input.
 */
export const PasswordField: React.FC<FieldProps> = (props: FieldProps) => {
  const {
    idSchema,
    uiSchema,
    registry: {
      fields: { StringField }
    }
  } = props;
  const [showPassword, setShowPassword] = React.useState(false);

  return (
    <div className="elyra-passwordField">
      <StringField
        {...props}
        idSchema={idSchema}
        uiSchema={{
          ...uiSchema,
          'ui:widget': showPassword ? undefined : 'password'
        }}
      />
      <button
        className="elyra-passwordFieldButton"
        onClick={(): void => setShowPassword(!showPassword)}
      >
        {showPassword ? <viewOffIcon.react /> : <viewIcon.react />}
      </button>
    </div>
  );
};
