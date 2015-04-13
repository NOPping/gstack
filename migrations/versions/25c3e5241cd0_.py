#!/usr/bin/env python
# encoding: utf-8
#
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
#

"""empty message

Revision ID: 25c3e5241cd0
Revises: 76bb287a37d
Create Date: 2014-07-27 16:19:12.634404

"""

# revision identifiers, used by Alembic.
revision = '25c3e5241cd0'
down_revision = '76bb287a37d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('accesstoken',
                  sa.Column(
                      'id_token',
                      sa.String(length=1000),
                      nullable=True
                  )
                  )

    op.add_column('refreshtoken',
                  sa.Column(
                      'id_token',
                      sa.String(length=1000),
                      nullable=True
                  )
                  )


def downgrade():
    pass
