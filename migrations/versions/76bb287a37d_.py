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

Revision ID: 76bb287a37d
Revises: None
Create Date: 2014-06-16 19:15:05.475000

"""

# revision identifiers, used by Alembic.
revision = '76bb287a37d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('accesstoken',
                    sa.Column(
                        'access_token',
                        sa.String(length=255),
                        nullable=False),
                    sa.Column(
                        'client_id',
                        sa.String(length=255),
                        nullable=True),
                    sa.Column(
                        'expires_in',
                        sa.String(length=10),
                        nullable=True),
                    sa.Column(
                        'data',
                        sa.String(length=500),
                        nullable=True),
                    sa.PrimaryKeyConstraint('access_token'),
                    sa.UniqueConstraint('client_id')
                    )
    op.create_table('client',
                    sa.Column('client_id',
                              sa.String(length=255),
                              nullable=False),
                    sa.Column(
                        'client_secret',
                        sa.String(length=255),
                        nullable=True),
                    sa.PrimaryKeyConstraint('client_id'),
                    sa.UniqueConstraint('client_secret')
                    )
    op.create_table('refreshtoken',
                    sa.Column(
                        'refresh_token',
                        sa.String(length=255),
                        nullable=False),
                    sa.Column(
                        'client_id',
                        sa.String(length=255),
                        nullable=True),
                    sa.Column(
                        'data',
                        sa.String(length=500),
                        nullable=True),
                    sa.PrimaryKeyConstraint('refresh_token'),
                    sa.UniqueConstraint('client_id')
                    )


def downgrade():
    pass
