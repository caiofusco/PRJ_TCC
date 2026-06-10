USE oficina_ai;

INSERT INTO users (name, email, password_hash, role, specialties, status) VALUES
('Administrador', 'admin@oficina.local', 'pbkdf2:sha256:260000$adminseed$28e6f4694241c1e3d35f2102983a5369ad37973230df117e24b258ef2c213e05', 'ADMIN', NULL, 'ATIVO'),
('Atendente', 'atendente@oficina.local', 'pbkdf2:sha256:260000$attseed$1d004596c6052db59585f3828981736966b488a9cd389a1121d91389d1d74d2c', 'ATENDENTE', NULL, 'ATIVO'),
('Marcos Silva', 'marcos@oficina.local', 'pbkdf2:sha256:260000$techseed$a48e5b48e0386c27345ad626b40c06761a5965d5c56c5d91b05e0d0313621a21', 'TECNICO', 'diagnóstico eletrônico, ecu, remap, injeção eletrônica', 'ATIVO'),
('Rafael Costa', 'rafael@oficina.local', 'pbkdf2:sha256:260000$techseed$a48e5b48e0386c27345ad626b40c06761a5965d5c56c5d91b05e0d0313621a21', 'TECNICO', 'troca de óleo, freios, revisão, suspensão, manutenção preventiva', 'ATIVO');

INSERT INTO services (name, description, category, base_price, estimated_minutes, active) VALUES
('Diagnóstico eletrônico', 'Leitura de módulos, falhas e parâmetros do veículo.', 'diagnóstico', 180.00, 60, TRUE),
('Remap de ECU', 'Ajuste de mapas de injeção e performance com validação.', 'ecu', 850.00, 180, TRUE),
('Limpeza de bicos injetores', 'Teste, limpeza e equalização dos bicos injetores.', 'injeção', 320.00, 120, TRUE),
('Troca de óleo e filtros', 'Substituição de óleo, filtro de óleo e inspeção básica.', 'manutenção preventiva', 120.00, 45, TRUE),
('Revisão de freios', 'Inspeção de pastilhas, discos, fluido e sistema de frenagem.', 'freios', 250.00, 90, TRUE);

INSERT INTO clients (name, cpf_cnpj, phone, email, address, status) VALUES
('Sofia Andrade', '123.456.789-10', '(21) 99999-1000', 'sofia@email.com', 'Rio de Janeiro - RJ', 'ATIVO'),
('Bruno Lima', '234.567.890-11', '(21) 98888-2000', 'bruno@email.com', 'Niterói - RJ', 'ATIVO'),
('Carla Menezes', '345.678.901-12', '(21) 97777-3000', 'carla@email.com', 'São Gonçalo - RJ', 'ATIVO');

INSERT INTO vehicles (plate, brand, model, year, color, client_id) VALUES
('ABC1D23', 'Volkswagen', 'Golf TSI', 2018, 'Prata', 1),
('RJO2E45', 'Fiat', 'Toro Diesel', 2021, 'Preta', 2),
('KAI3F67', 'Chevrolet', 'Onix', 2020, 'Branco', 3);

INSERT INTO products (name, description, quantity, min_quantity, unit_price, active) VALUES
('Óleo 5W30 sintético', 'Lubrificante 1L', 16, 5, 48.90, TRUE),
('Filtro de óleo', 'Filtro linha leve', 8, 4, 39.90, TRUE),
('Aditivo de radiador', 'Aditivo concentrado', 3, 4, 34.90, TRUE),
('Jogo de velas', 'Jogo com 4 unidades', 2, 2, 189.90, TRUE);
